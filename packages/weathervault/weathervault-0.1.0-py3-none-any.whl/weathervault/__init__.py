"""
weathervault: Obtain Polars DataFrames of historical weather data from the NCEI weather database.
"""

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # pragma: no cover
    from importlib_metadata import PackageNotFoundError, version

from weathervault._constants import (
    BASE_URL,
    COUNTRY_CODES,
    ISO_COUNTRY_NAMES,
    US_STATE_NAMES,
    country,
    state,
)
from weathervault._registry import station
from weathervault.stations import (
    get_countries,
    get_inventory,
    get_station_metadata,
    search_stations,
)
from weathervault.weather import get_weather_data

try:  # pragma: no cover
    __version__ = version("weathervault")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

__all__ = [
    # Main functions
    "get_weather_data",
    "get_station_metadata",
    "search_stations",
    "get_inventory",
    "get_countries",
    # Station registry for autocomplete
    "station",
    # Constants
    "BASE_URL",
    "COUNTRY_CODES",
    "ISO_COUNTRY_NAMES",
    "US_STATE_NAMES",
    "country",
    "state",
    # Version
    "__version__",
]
