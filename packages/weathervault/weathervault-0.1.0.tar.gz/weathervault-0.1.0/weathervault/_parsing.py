"""ISD data format parsing utilities."""

from __future__ import annotations

import gzip
import io
from typing import TYPE_CHECKING

import polars as pl

from weathervault._constants import (
    MANDATORY_COLUMN_NAMES,
    MANDATORY_COLUMN_WIDTHS,
    MISSING_VALUES,
    SCALE_FACTORS,
)

if TYPE_CHECKING:
    pass


def parse_isd_line(line: str) -> dict:
    """
    Parse a single line of ISD data into a dictionary.

    Parameters
    ----------
    line
        A single line from an ISD data file.

    Returns
    -------
    dict
        Dictionary containing parsed values from the mandatory data section.
    """
    values = {}
    pos = 0

    for _i, (name, width) in enumerate(
        zip(MANDATORY_COLUMN_NAMES, MANDATORY_COLUMN_WIDTHS, strict=True)
    ):
        if pos + width > len(line):
            # Line is shorter than expected, fill with None
            values[name] = None
        else:
            raw_value = line[pos : pos + width].strip()
            values[name] = raw_value if raw_value else None
        pos += width

    return values


def parse_isd_data(data: bytes | str) -> pl.DataFrame:
    """
    Parse ISD format data (gzipped or plain text) into a Polars DataFrame.

    Parameters
    ----------
    data
        The raw ISD data as bytes (possibly gzipped) or string.

    Returns
    -------
    pl.DataFrame
        DataFrame containing the parsed weather observations.
    """
    # Handle gzipped data
    if isinstance(data, bytes):
        try:
            # Try to decompress as gzip
            with gzip.GzipFile(fileobj=io.BytesIO(data)) as f:
                text = f.read().decode("utf-8", errors="replace")
        except gzip.BadGzipFile:
            # Not gzipped, decode directly
            text = data.decode("utf-8", errors="replace")
    else:
        text = data

    lines = text.strip().split("\n")
    if not lines:
        return _empty_weather_dataframe()

    # Parse each line
    records = []
    for line in lines:
        if line.strip():
            record = parse_isd_line(line)
            records.append(record)

    if not records:
        return _empty_weather_dataframe()

    # Create DataFrame from records
    df = pl.DataFrame(records)

    return df


def process_weather_data(
    df: pl.DataFrame,
    *,
    tz_name: str | None = None,
    convert_to_local: bool = True,
    temp_unit: str = "celsius",
    stn_metadata: dict | None = None,
) -> pl.DataFrame:
    """
    Process raw parsed ISD data into a clean weather DataFrame.

    Parameters
    ----------
    df
        Raw DataFrame from parse_isd_data.
    tz_name
        Timezone name for the station (e.g., "America/New_York").
        Used for converting UTC times to local time.
    convert_to_local
        Whether to convert times from UTC to local time. Default is True.
    temp_unit
        Temperature unit for output: "celsius" or "fahrenheit". Default is "celsius".
    stn_metadata
        Optional dictionary containing station metadata to include in output.
        Should contain keys: name, country, state, icao, lat, lon, elev.

    Returns
    -------
    pl.DataFrame
        Processed DataFrame with clean, usable weather data.
    """
    if df.height == 0:
        return _empty_processed_dataframe()

    # Convert numeric columns
    df = df.with_columns(
        [
            pl.col("year").cast(pl.Int32, strict=False),
            pl.col("month").cast(pl.Int32, strict=False),
            pl.col("day").cast(pl.Int32, strict=False),
            pl.col("hour").cast(pl.Int32, strict=False),
            pl.col("minute").cast(pl.Int32, strict=False),
            pl.col("wind_direction").cast(pl.Int32, strict=False),
            pl.col("wind_speed").cast(pl.Int32, strict=False),
            pl.col("ceiling_height").cast(pl.Int32, strict=False),
            pl.col("visibility").cast(pl.Int32, strict=False),
            pl.col("temp").cast(pl.Int32, strict=False),
            pl.col("dew_point").cast(pl.Int32, strict=False),
            pl.col("sea_level_pressure").cast(pl.Int32, strict=False),
        ]
    )

    # Create station ID
    df = df.with_columns(pl.concat_str([pl.col("usaf"), pl.lit("-"), pl.col("wban")]).alias("id"))

    # Create datetime column (UTC)
    df = df.with_columns(
        pl.datetime(
            year=pl.col("year"),
            month=pl.col("month"),
            day=pl.col("day"),
            hour=pl.col("hour"),
            minute=pl.col("minute"),
            time_zone="UTC",
        ).alias("time_utc")
    )

    # Replace missing values with null
    df = df.with_columns(
        [
            pl.when(pl.col("wind_direction") == MISSING_VALUES["wind_direction"])
            .then(None)
            .otherwise(pl.col("wind_direction"))
            .alias("wind_direction"),
            pl.when(pl.col("wind_speed") == MISSING_VALUES["wind_speed"])
            .then(None)
            .otherwise(pl.col("wind_speed"))
            .alias("wind_speed"),
            pl.when(pl.col("ceiling_height") == MISSING_VALUES["ceiling_height"])
            .then(None)
            .otherwise(pl.col("ceiling_height"))
            .alias("ceiling_height"),
            pl.when(pl.col("visibility") == MISSING_VALUES["visibility"])
            .then(None)
            .otherwise(pl.col("visibility"))
            .alias("visibility"),
            pl.when(pl.col("temp") == MISSING_VALUES["temp"])
            .then(None)
            .otherwise(pl.col("temp"))
            .alias("temp"),
            pl.when(pl.col("dew_point") == MISSING_VALUES["dew_point"])
            .then(None)
            .otherwise(pl.col("dew_point"))
            .alias("dew_point"),
            pl.when(pl.col("sea_level_pressure") == MISSING_VALUES["sea_level_pressure"])
            .then(None)
            .otherwise(pl.col("sea_level_pressure"))
            .alias("sea_level_pressure"),
        ]
    )

    # Apply scale factors
    df = df.with_columns(
        [
            (pl.col("wind_speed").cast(pl.Float64) / SCALE_FACTORS["wind_speed"]).alias(
                "wind_speed"
            ),
            (pl.col("temp").cast(pl.Float64) / SCALE_FACTORS["temp"]).alias("temp"),
            (pl.col("dew_point").cast(pl.Float64) / SCALE_FACTORS["dew_point"]).alias("dew_point"),
            (
                pl.col("sea_level_pressure").cast(pl.Float64) / SCALE_FACTORS["sea_level_pressure"]
            ).alias("sea_level_pressure"),
        ]
    )

    # Calculate relative humidity using the August-Roche-Magnus approximation
    df = df.with_columns(
        (
            100.0
            * (
                ((17.625 * pl.col("dew_point")) / (243.04 + pl.col("dew_point"))).exp()
                / ((17.625 * pl.col("temp")) / (243.04 + pl.col("temp"))).exp()
            )
        )
        .round(1)
        .alias("relative_humidity")
    )

    # Convert temperature if requested (data is in Celsius by default)
    if temp_unit == "fahrenheit":
        df = df.with_columns(
            [
                ((pl.col("temp") * 9 / 5) + 32).round(1).alias("temp"),
                ((pl.col("dew_point") * 9 / 5) + 32).round(1).alias("dew_point"),
            ]
        )
    elif temp_unit == "kelvin":
        df = df.with_columns(
            [
                (pl.col("temp") + 273.15).round(2).alias("temp"),
                (pl.col("dew_point") + 273.15).round(2).alias("dew_point"),
            ]
        )

    # Handle time conversion to local
    if convert_to_local and tz_name:
        # Convert UTC datetime to local time
        df = df.with_columns(pl.col("time_utc").dt.convert_time_zone(tz_name).alias("time"))
    else:
        df = df.with_columns(pl.col("time_utc").alias("time"))

    # Build column list for final selection
    columns = [
        pl.col("id"),
        pl.col("time"),
        pl.col("temp"),
        pl.col("dew_point"),
        pl.col("relative_humidity").alias("rh"),
        pl.col("wind_direction").alias("wd"),
        pl.col("wind_speed").alias("ws"),
        pl.col("sea_level_pressure").alias("atmos_pres"),
        pl.col("ceiling_height").alias("ceil_hgt"),
        pl.col("visibility"),
    ]

    # Add station metadata columns if provided
    if stn_metadata is not None:
        df = df.with_columns(
            [
                pl.lit(stn_metadata["name"]).alias("name"),
                pl.lit(stn_metadata["country"]).alias("country"),
                pl.lit(stn_metadata["state"]).alias("state"),
                pl.lit(stn_metadata["icao"]).alias("icao"),
                pl.lit(stn_metadata["lat"]).alias("lat"),
                pl.lit(stn_metadata["lon"]).alias("lon"),
                pl.lit(stn_metadata["elev"]).alias("elev"),
            ]
        )
        columns.extend(
            [
                pl.col("name"),
                pl.col("country"),
                pl.col("state"),
                pl.col("icao"),
                pl.col("lat"),
                pl.col("lon"),
                pl.col("elev"),
            ]
        )

    # Select and rename final columns
    result = df.select(columns)

    return result


def _empty_weather_dataframe() -> pl.DataFrame:
    """Create an empty DataFrame with the raw ISD column schema."""
    return pl.DataFrame(schema=dict.fromkeys(MANDATORY_COLUMN_NAMES, pl.Utf8))


def _empty_processed_dataframe(incl_stn_info: bool = False) -> pl.DataFrame:
    """Create an empty DataFrame with the processed weather schema.

    Parameters
    ----------
    incl_stn_info
        Whether to include station metadata columns in the schema.
    """
    schema = {
        "id": pl.Utf8,
        "time": pl.Datetime("us", "UTC"),
        "temp": pl.Float64,
        "dew_point": pl.Float64,
        "rh": pl.Float64,
        "wd": pl.Int32,
        "ws": pl.Float64,
        "atmos_pres": pl.Float64,
        "ceil_hgt": pl.Int32,
        "visibility": pl.Int32,
    }

    if incl_stn_info:
        schema.update(
            {
                "name": pl.Utf8,
                "country": pl.Utf8,
                "state": pl.Utf8,
                "icao": pl.Utf8,
                "lat": pl.Float64,
                "lon": pl.Float64,
                "elev": pl.Float64,
            }
        )

    return pl.DataFrame(schema=schema)
