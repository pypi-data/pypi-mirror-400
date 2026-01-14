"""Station metadata and inventory functions."""

from __future__ import annotations

import io
from typing import TYPE_CHECKING

import httpx
import polars as pl
from timezonefinder import TimezoneFinder

from weathervault._constants import BASE_URL, COUNTRY_CODES, FIPS_TO_ISO

if TYPE_CHECKING:
    pass

# Module-level cache for station data (always stores version WITH timezone)
_station_metadata_cache: pl.DataFrame | None = None
_station_metadata_cache_has_tz: bool = False
_inventory_cache: pl.DataFrame | None = None
_tf: TimezoneFinder | None = None


def _get_timezone_finder() -> TimezoneFinder:
    """Get or create the TimezoneFinder instance."""
    global _tf
    if _tf is None:
        _tf = TimezoneFinder()
    return _tf


def get_station_metadata(
    *,
    include_timezone: bool = True,
    force_refresh: bool = False,
) -> pl.DataFrame:
    """
    Get metadata for all weather stations.

    Downloads and parses the ISD history file containing information about all weather stations in
    the database.

    Parameters
    ----------
    include_timezone
        Whether to look up timezone names based on station coordinates. This adds a `tz_name`
        column. Default is `True`.
    force_refresh
        Force re-download of station data even if cached. Default is `False`.

    Returns
    -------
    pl.DataFrame
        A DataFrame with station metadata including:

        - `id`: Station ID (USAF-WBAN format)
        - `usaf`: USAF station identifier
        - `wban`: WBAN station identifier
        - `name`: Station name
        - `country_code`: ISO 3166-1 alpha-2 country code
        - `country`: Country name
        - `state`: US state code (if applicable)
        - `icao`: ICAO identifier
        - `lat`: Latitude in degrees
        - `lon`: Longitude in degrees
        - `elev`: Elevation in meters
        - `begin_date`: Date of first available data
        - `end_date`: Date of last available data
        - `tz_name`: Timezone name (if `include_timezone=` is `True`)

    Examples
    --------
    Get metadata for all weather stations:

    ```{python}
    import weathervault as wv
    stations = wv.get_station_metadata()
    stations.head()
    ```
    """
    global _station_metadata_cache, _station_metadata_cache_has_tz

    # If we have a cached version with timezone, we can serve both cases
    if _station_metadata_cache is not None and not force_refresh:
        if _station_metadata_cache_has_tz:
            # Cache has timezone: can serve both requests
            if include_timezone:
                return _station_metadata_cache
            else:
                # Return without tz_name column
                return _station_metadata_cache.drop("tz_name")
        elif not include_timezone:
            # Cache doesn't have timezone, and we don't need it
            return _station_metadata_cache
        # Otherwise, cache doesn't have timezone but we need it: refetch

    url = f"{BASE_URL}/isd-history.csv"

    with httpx.Client(timeout=60.0) as client:
        response = client.get(url)
        response.raise_for_status()

    df = pl.read_csv(
        io.BytesIO(response.content),
        schema_overrides={
            "USAF": pl.Utf8,
            "WBAN": pl.Utf8,
            "BEGIN": pl.Utf8,
            "END": pl.Utf8,
        },
    )

    # Rename columns to be more Pythonic
    df = df.rename(
        {
            "USAF": "usaf",
            "WBAN": "wban",
            "STATION NAME": "name",
            "CTRY": "country_code",
            "STATE": "state",
            "ICAO": "icao",
            "LAT": "lat",
            "LON": "lon",
            "ELEV(M)": "elev",
            "BEGIN": "begin_date",
            "END": "end_date",
        }
    )

    # Create station ID and parse dates
    df = df.with_columns(
        pl.concat_str([pl.col("usaf"), pl.lit("-"), pl.col("wban")]).alias("id"),
        pl.col("begin_date").str.to_date("%Y%m%d").alias("begin_date"),
        pl.col("end_date").str.to_date("%Y%m%d").alias("end_date"),
        # Ensure lat/lon/elev are numeric (they may have + prefix in CSV)
        pl.col("lat").cast(pl.Float64, strict=False),
        pl.col("lon").cast(pl.Float64, strict=False),
        pl.col("elev").cast(pl.Float64, strict=False),
    )

    # Replace missing value sentinel (-999.0, -999.9) with null for elevation
    df = df.with_columns(
        pl.when(pl.col("elev") < -900).then(None).otherwise(pl.col("elev")).alias("elev")
    )

    # Add country name from FIPS code (before conversion to ISO)
    df = df.with_columns(
        pl.col("country_code").replace_strict(COUNTRY_CODES, default=None).alias("country")
    )

    # Convert FIPS country codes to ISO codes
    df = df.with_columns(
        pl.col("country_code").replace_strict(FIPS_TO_ISO, default=None).alias("country_code")
    )

    # Reorder columns
    column_order = [
        "id",
        "usaf",
        "wban",
        "name",
        "country_code",
        "country",
        "state",
        "icao",
        "lat",
        "lon",
        "elev",
        "begin_date",
        "end_date",
    ]

    if include_timezone:
        # Look up timezone for each station based on coordinates
        tf = _get_timezone_finder()

        def get_tz(lat: float | None, lon: float | None) -> str | None:
            if lat is None or lon is None:
                return None
            try:
                return tf.timezone_at(lat=lat, lng=lon)
            except Exception:
                return None

        tz_names = [
            get_tz(lat, lon)
            for lat, lon in zip(df["lat"].to_list(), df["lon"].to_list(), strict=True)
        ]
        df = df.with_columns(pl.Series("tz_name", tz_names))
        column_order.append("tz_name")

    df = df.select(column_order)

    # Cache the result and track whether it has timezone
    _station_metadata_cache = df
    _station_metadata_cache_has_tz = include_timezone
    return df


def get_inventory(*, force_refresh: bool = False) -> pl.DataFrame:
    """
    Get the data inventory for all stations and years.

    Downloads and parses the ISD inventory file containing record counts for each station by year
    and month.

    Parameters
    ----------
    force_refresh
        Force re-download of inventory data even if cached. Default is `False`.

    Returns
    -------
    pl.DataFrame
        A DataFrame with inventory information including:

        - `id`: Station ID (USAF-WBAN format)
        - `usaf`: USAF station identifier
        - `wban`: WBAN station identifier
        - `year`: Year of data
        - `jan` through `dec`: Record counts for each month
        - `total`: Total records for the year

    Examples
    --------
    Get data inventory for all stations:

    ```{python}
    import weathervault as wv
    inventory = wv.get_inventory()
    inventory.filter(pl.col("id") == "725030-14732")
    ```
    """
    global _inventory_cache

    if _inventory_cache is not None and not force_refresh:
        return _inventory_cache

    url = f"{BASE_URL}/isd-inventory.csv"

    with httpx.Client(timeout=60.0) as client:
        response = client.get(url)
        response.raise_for_status()

    df = pl.read_csv(
        io.BytesIO(response.content),
        schema_overrides={
            "USAF": pl.Utf8,
            "WBAN": pl.Utf8,
        },
    )

    # Rename columns
    df = df.rename(
        {
            "USAF": "usaf",
            "WBAN": "wban",
            "YEAR": "year",
            "JAN": "jan",
            "FEB": "feb",
            "MAR": "mar",
            "APR": "apr",
            "MAY": "may",
            "JUN": "jun",
            "JUL": "jul",
            "AUG": "aug",
            "SEP": "sep",
            "OCT": "oct",
            "NOV": "nov",
            "DEC": "dec",
        }
    )

    # Create station ID and calculate total
    df = df.with_columns(
        pl.concat_str([pl.col("usaf"), pl.lit("-"), pl.col("wban")]).alias("id"),
        (
            pl.col("jan")
            + pl.col("feb")
            + pl.col("mar")
            + pl.col("apr")
            + pl.col("may")
            + pl.col("jun")
            + pl.col("jul")
            + pl.col("aug")
            + pl.col("sep")
            + pl.col("oct")
            + pl.col("nov")
            + pl.col("dec")
        ).alias("total"),
    )

    # Reorder columns
    df = df.select(
        [
            "id",
            "usaf",
            "wban",
            "year",
            "jan",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
            "total",
        ]
    )

    _inventory_cache = df
    return df


def search_stations(
    *,
    name: str | None = None,
    country: str | None = None,
    country_code: str | None = None,
    state: str | None = None,
    lat_range: tuple[float, float] | None = None,
    lon_range: tuple[float, float] | None = None,
    has_recent_data: bool = False,
) -> pl.DataFrame:
    """
    Search for weather stations matching specified criteria.

    Parameters
    ----------
    name
        Search for stations with names containing this string (case-insensitive).
    country
        Filter by country name (case-insensitive, partial match).
    country_code
        Filter by ISO 3166-1 alpha-2 country code (e.g., `"US"`, `"GB"`, `"FR"`).
        For convenience, you can also use the `wv.country` shorthand:
        `wv.country.US`, `wv.country.GB`, `wv.country.DE`, etc.
    state
        Filter by US state or territory code (exact match, e.g., `"CA"`, `"NY"`, `"TX"`).
        For convenience, you can also use the `wv.state` shorthand:
        `wv.state.CA`, `wv.state.NY`, `wv.state.TX`, etc.
    lat_range
        Filter by latitude range as (min_lat, max_lat).
    lon_range
        Filter by longitude range as (min_lon, max_lon).
    has_recent_data
        If `True`, only return stations with data in the current or previous year.

    Returns
    -------
    pl.DataFrame
        A DataFrame of stations matching the search criteria.

    Examples
    --------
    Search for stations in California using the state shorthand:

    ```{python}
    import weathervault as wv

    # Using wv.state shorthand (provides autocomplete)
    ca_stations = wv.search_stations(state=wv.state.CA)

    ca_stations
    ```

    Search by country code using the convenient shorthand:

    ```{python}
    # Using wv.country shorthand (provides autocomplete)
    de_stations = wv.search_stations(country_code=wv.country.DE)

    de_stations
    ```

    Combine state and country filters:

    ```{python}
    # Find stations in California, US
    us_ca = wv.search_stations(
        country_code=wv.country.US,
        state=wv.state.CA
    )

    us_ca
    ```

    Search for stations within a bounding box:

    ```{python}
    within = wv.search_stations(
        lat_range=(37.0, 38.0),
        lon_range=(-122.5, -121.5)
    )

    within
    ```
    """
    df = get_station_metadata()

    if name is not None:
        df = df.filter(pl.col("name").str.to_lowercase().str.contains(name.lower()))

    if country is not None:
        df = df.filter(pl.col("country").str.to_lowercase().str.contains(country.lower()))

    if country_code is not None:
        # Filter by ISO country code (DataFrame now contains ISO codes)
        iso_code = country_code.upper()
        df = df.filter(pl.col("country_code") == iso_code)

    if state is not None:
        df = df.filter(pl.col("state") == state.upper())

    if lat_range is not None:
        min_lat, max_lat = lat_range
        df = df.filter((pl.col("lat") >= min_lat) & (pl.col("lat") <= max_lat))

    if lon_range is not None:
        min_lon, max_lon = lon_range
        df = df.filter((pl.col("lon") >= min_lon) & (pl.col("lon") <= max_lon))

    if has_recent_data:
        from datetime import date

        current_year = date.today().year
        cutoff_date = date(current_year - 1, 1, 1)
        df = df.filter(pl.col("end_date") >= cutoff_date)

    return df


def get_years_for_station(station_id: str) -> list[int]:
    """
    Get the list of years for which a station has data.

    Parameters
    ----------
    station_id
        The station ID in USAF-WBAN format (e.g., `"725030-14732"`).

    Returns
    -------
    list[int]
        List of years with available data.

    Examples
    --------
    Get available years for a specific station:

    ```{python}
    import weathervault as wv

    years = wv.get_years_for_station("725030-14732")

    years
    ```
    """
    inventory = get_inventory()
    station_data = inventory.filter(pl.col("id") == station_id)

    if station_data.height == 0:
        return []

    return sorted(station_data["year"].to_list())


def get_countries() -> pl.DataFrame:
    """
    Get a DataFrame of country codes and names.

    Returns
    -------
    pl.DataFrame
        A DataFrame with columns:

        - country_code: ISO 3166-1 alpha-2 country code
        - country: Country name

    Examples
    --------
    Get a list of all countries with weather stations:

    ```{python}
    import weathervault as wv

    countries = wv.get_countries()

    countries
    ```
    """
    # Create mapping from FIPS to ISO codes with country names
    iso_codes = []
    country_names = []

    for fips_code, country_name in COUNTRY_CODES.items():
        if fips_code in FIPS_TO_ISO:
            iso_codes.append(FIPS_TO_ISO[fips_code])
            country_names.append(country_name)

    return pl.DataFrame(
        {
            "country_code": iso_codes,
            "country": country_names,
        }
    ).sort("country")
