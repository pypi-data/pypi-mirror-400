"""Main weather data retrieval functions."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

import httpx
import polars as pl

from weathervault._constants import BASE_URL
from weathervault._parsing import _empty_processed_dataframe, parse_isd_data, process_weather_data
from weathervault.stations import get_station_metadata, get_years_for_station

if TYPE_CHECKING:
    pass


def _normalize_temp_unit(temp_unit: str) -> str | None:
    """
    Normalize temperature unit string to standard form.

    Parameters
    ----------
    temp_unit
        Temperature unit string (e.g., `"c"`, `"C"`, `"celsius"`, `"Celsius"`).

    Returns
    -------
    str | None
        Normalized form ("celsius", "fahrenheit", or "kelvin"), or None if invalid.
    """
    unit = temp_unit.lower().strip()
    if unit in ("c", "celsius"):
        return "celsius"
    elif unit in ("f", "fahrenheit"):
        return "fahrenheit"
    elif unit in ("k", "kelvin"):
        return "kelvin"
    return None


def get_weather_data(
    station_id: str,
    years: int | list[int] | None = None,
    *,
    convert_to_local: bool = True,
    temp_unit: str = "celsius",
    make_hourly: bool = False,
    cache_dir: str | Path | None = None,
    incl_stn_info: bool = False,
) -> pl.DataFrame:
    """
    Get weather data for a meteorological station.

    Downloads and parses weather observation data from NOAA's Integrated
    Surface Database (ISD) for the specified station and years.

    Parameters
    ----------
    station_id
        Station identifier in USAF-WBAN format (e.g., "725030-14732"). Use `search_stations()` or
        `get_station_metadata()` to find station IDs.
    years
        Year or list of years to retrieve data for. If `None`, retrieves all available years for
        the station.
    convert_to_local
        Whether to convert times from UTC to the station's local time. Default is `True`.
    temp_unit
        Temperature unit for output. Accepts `"c"`/`"celsius"`, `"f"`/`"fahrenheit"`, or
        `"k"`/`"kelvin"` (case-insensitive). Default is `"c"` (Celsius).
    make_hourly
        If `True`, resample data to hourly intervals, taking the first observation of each hour and
        filling missing hours with `None` values. Default is `False`.
    cache_dir
        Directory to cache downloaded data files. Options are: (1) `None` (default) for downloading
        data to memory without saving to disk (will check current working directory for existing
        cached files first), (2) `"."` saves to and loads from current working directory, and (3) a
        path string serving as a custom directory path for caching files. Cached files are named as
        `"{station_id}-{year}.gz"`.
    incl_stn_info
        Whether to include station metadata in the output. When True, adds columns for station name,
        country, state, ICAO code, latitude, longitude, and elevation. Default is `False`.

    Returns
    -------
    pl.DataFrame
        A DataFrame with weather observations containing:

        - `id`: Station identifier
        - `time`: Observation time (local time if `convert_to_local=True`, else UTC)
        - `temp`: Air temperature (Celsius, Fahrenheit, or Kelvin based on `temp_unit=`)
        - `dew_point`: Dew point temperature
        - `rh`: Relative humidity (percentage)
        - `wd`: Wind direction in degrees (`0`-`360`, direction wind is blowing from)
        - `ws`: Wind speed in meters per second
        - `atmos_pres`: Atmospheric pressure at sea level (hectopascals)
        - `ceil_hgt`: Ceiling height in meters (`22000` is taken as unlimited)
        - `visibility`: Visibility in meters (max is `16000`)

        If incl_stn_info=True, also includes:

        - `name`: Station name
        - `country`: Country name
        - `state`: State/region code (if applicable)
        - `icao`: ICAO identifier
        - `lat`: Latitude in degrees
        - `lon`: Longitude in degrees
        - `elev`: Elevation in meters above sea level

    Examples
    --------
    Get weather data for JFK Airport (New York) for 2023:

    ```{python}
    import weathervault as wv

    weather = wv.get_weather_data("744860-94789", years=2023)
    weather.head()
    ```

    Get data for multiple years with Fahrenheit temperatures:

    ```{python}
    weather = wv.get_weather_data(
        "725030-14732",  # LaGuardia Airport
        years=[2022, 2023],
        temp_unit="fahrenheit"
    )

    weather
    ```

    Get hourly data (resampled):

    ```{python}
    weather = wv.get_weather_data(
        "724050-13743",  # Washington Reagan Airport
        years=2023,
        make_hourly=True
    )

    weather
    ```

    Cache data to current directory for offline use:

    ```{python}
    weather = wv.get_weather_data(
        "725030-14732",
        years=2023,
        cache_dir="."  # Saves to current working directory
    )

    # Subsequent calls will automatically use the cached file
    weather = wv.get_weather_data("725030-14732", years=2023)  # Loads from cache

    weather
    ```

    Include station metadata in the output:

    ```{python}
    weather = wv.get_weather_data(
        "725030-14732",
        years=2023,
        incl_stn_info=True
    )

    weather[["name", "country", "lat", "lon"]].head(1)
    ```
    """
    # Normalize and validate temperature unit
    temp_unit_normalized = _normalize_temp_unit(temp_unit)
    if temp_unit_normalized is None:
        raise ValueError("temp_unit must be 'c', 'celsius', 'f', 'fahrenheit', 'k', or 'kelvin'")

    # Get station metadata to find timezone and potentially include in output
    stations = get_station_metadata()
    station_info = stations.filter(pl.col("id") == station_id)

    if station_info.height == 0:
        raise ValueError(
            f"Station '{station_id}' not found in metadata. "
            "Use search_stations() to find valid station IDs."
        )

    tz_name = station_info["tz_name"][0] if "tz_name" in station_info.columns else None

    # Extract station metadata if requested
    stn_metadata = None
    if incl_stn_info:
        stn_metadata = {
            "name": station_info["name"][0],
            "country": station_info["country"][0],
            "state": station_info["state"][0],
            "icao": station_info["icao"][0],
            "lat": station_info["lat"][0],
            "lon": station_info["lon"][0],
            "elev": station_info["elev"][0],
        }

    # Determine years to fetch
    if years is None:
        years_to_fetch = get_years_for_station(station_id)
        if not years_to_fetch:
            raise ValueError(f"No data available for station '{station_id}'")
    elif isinstance(years, int):
        years_to_fetch = [years]
    else:
        years_to_fetch = list(years)

    # Set up cache directory if specified
    # Special case: "." means use current working directory
    if cache_dir == ".":
        cache_path = Path.cwd()
    elif cache_dir:
        cache_path = Path(cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)
    else:
        cache_path = None

    # Download and parse data for each year
    all_data: list[pl.DataFrame] = []

    for year in years_to_fetch:
        data = _fetch_year_data(station_id, year, cache_path)
        if data is not None:
            df = parse_isd_data(data)
            if df.height > 0:
                processed = process_weather_data(
                    df,
                    tz_name=tz_name,
                    convert_to_local=convert_to_local,
                    temp_unit=temp_unit_normalized,
                    stn_metadata=stn_metadata,
                )
                all_data.append(processed)

    if not all_data:
        return _empty_processed_dataframe(incl_stn_info=incl_stn_info)

    # Combine all years
    result = pl.concat(all_data)

    # Sort by time
    result = result.sort("time")

    # Filter to requested years (in case of edge cases at year boundaries)
    result = result.filter(pl.col("time").dt.year().is_in(years_to_fetch))

    # Optionally resample to hourly
    if make_hourly:
        result = _make_hourly(
            result, years_to_fetch, tz_name if convert_to_local else "UTC", incl_stn_info
        )

    return result


def _fetch_year_data(
    station_id: str,
    year: int,
    cache_path: Path | None = None,
) -> bytes | None:
    """
    Fetch weather data for a station and year.

    First checks for cached files in:

    1. The specified cache directory (if provided)
    2. The current working directory (always checked)

    If not found locally, downloads from NCEI and caches if `cache_path=` is set.

    Parameters
    ----------
    station_id
        Station ID in USAF-WBAN format.
    year
        Year to fetch.
    cache_path
        Optional path to cache directory. If provided, downloaded files will be saved here. If
        `None`, files are not saved after download.

    Returns
    -------
    bytes | None
        Raw gzipped data bytes, or `None` if fetch failed.
    """
    filename = f"{station_id}-{year}.gz"

    # Check cache directory first (if provided)
    if cache_path:
        cached_file = cache_path / filename
        if cached_file.exists():
            return cached_file.read_bytes()

    # Always check current working directory for existing cached files
    # This allows offline use if files were previously downloaded
    cwd_cached_file = Path.cwd() / filename
    if cwd_cached_file.exists():
        return cwd_cached_file.read_bytes()

    # Download from NCEI
    url = f"{BASE_URL}/{year}/{filename}"

    try:
        with httpx.Client(timeout=120.0, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            data = response.content

            # Cache if directory specified
            if cache_path and data:
                cached_file = cache_path / filename
                cached_file.write_bytes(data)

            return data

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            # Data not available for this year
            return None
        raise
    except httpx.RequestError:
        # Network error
        return None


def _make_hourly(
    df: pl.DataFrame,
    years: list[int],
    tz_name: str | None,
    incl_stn_info: bool = False,
) -> pl.DataFrame:
    """
    Resample data to hourly intervals, filling missing hours.

    Parameters
    ----------
    df
        Weather DataFrame to resample.
    years
        List of years to ensure complete hourly coverage.
    tz_name
        Timezone name for the time column.

    Returns
    -------
    pl.DataFrame
        Resampled hourly DataFrame.
    """
    if df.height == 0:
        return df

    # Get station ID
    station_id = df["id"][0]

    # Truncate time to hour
    df = df.with_columns(pl.col("time").dt.truncate("1h").alias("time"))

    # Build aggregation list
    agg_cols = [
        pl.col("id").first(),
        pl.col("temp").first(),
        pl.col("dew_point").first(),
        pl.col("rh").first(),
        pl.col("wd").first(),
        pl.col("ws").first(),
        pl.col("atmos_pres").first(),
        pl.col("ceil_hgt").first(),
        pl.col("visibility").first(),
    ]

    # Add station metadata columns if present
    if incl_stn_info and "name" in df.columns:
        agg_cols.extend(
            [
                pl.col("name").first(),
                pl.col("country").first(),
                pl.col("state").first(),
                pl.col("icao").first(),
                pl.col("lat").first(),
                pl.col("lon").first(),
                pl.col("elev").first(),
            ]
        )

    # Take first observation of each hour
    df = df.group_by("time").agg(agg_cols)

    # Create complete hourly range for all years
    min_year = min(years)
    max_year = max(years)

    start_time = date(min_year, 1, 1)
    end_time = date(max_year, 12, 31)

    # Generate all hours in the range
    all_hours = pl.datetime_range(
        start=start_time,
        end=end_time,
        interval="1h",
        time_zone=tz_name,
        eager=True,
    )

    hours_df = pl.DataFrame({"time": all_hours})

    # Filter to only the requested years
    hours_df = hours_df.filter(pl.col("time").dt.year().is_in(years))

    # Join with actual data
    result = hours_df.join(df, on="time", how="left")

    # Fill station ID for missing rows
    result = result.with_columns(pl.lit(station_id).alias("id"))

    # Build column order
    columns = [
        "id",
        "time",
        "temp",
        "dew_point",
        "rh",
        "wd",
        "ws",
        "atmos_pres",
        "ceil_hgt",
        "visibility",
    ]

    # Add station metadata columns if present
    if incl_stn_info and "name" in result.columns:
        columns.extend(["name", "country", "state", "icao", "lat", "lon", "elev"])

    # Reorder columns
    result = result.select(columns)

    return result.sort("time")
