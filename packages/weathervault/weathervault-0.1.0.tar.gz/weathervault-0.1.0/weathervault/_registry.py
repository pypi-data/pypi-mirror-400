"""Station registry for IDE autocomplete support."""

from __future__ import annotations

import re
from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import polars as pl


def _sanitize_name(name: str) -> str:
    """Convert station name to valid Python identifier.

    Examples:
        "NEW YORK LAGUARDIA AP" -> "NEW_YORK_LAGUARDIA_AP"
        "JOHN F KENNEDY INTL" -> "JOHN_F_KENNEDY_INTL"
        "ST. LOUIS" -> "ST_LOUIS"
    """
    if not name:
        return "UNKNOWN"
    # Replace non-alphanumeric with underscore, collapse multiple underscores
    sanitized = re.sub(r"[^A-Z0-9]+", "_", name.upper())
    # Remove leading/trailing underscores
    sanitized = sanitized.strip("_")
    # Ensure it doesn't start with a number
    if sanitized and sanitized[0].isdigit():
        sanitized = "_" + sanitized
    return sanitized or "UNKNOWN"


@lru_cache(maxsize=1)
def _get_stations_df() -> pl.DataFrame:
    """Get station metadata (cached)."""
    from weathervault.stations import get_station_metadata

    return get_station_metadata(include_timezone=False)


class _StationNamespace:
    """A namespace that provides station IDs with autocomplete support.

    This class lazily loads station data and provides attribute access to station IDs organized by
    country and optionally state.
    """

    def __init__(
        self,
        stations: dict[str, str] | None = None,
        children: dict[str, _StationNamespace] | None = None,
    ):
        """Initialize namespace.

        Args:
            stations: Dict mapping sanitized names to station IDs
            children: Dict mapping child namespace names to child namespaces
        """
        self._stations = stations or {}
        self._children = children or {}

    def __getattr__(self, name: str) -> _StationNamespace | str:
        """Get a child namespace or station ID."""
        if name.startswith("_"):
            raise AttributeError(name)

        # Check children first (country codes, states)
        if name in self._children:
            return self._children[name]

        # Then check stations
        if name in self._stations:
            return self._stations[name]

        # Try case-insensitive match
        name_upper = name.upper()
        for key, value in self._children.items():
            if key.upper() == name_upper:
                return value
        for key, value in self._stations.items():
            if key.upper() == name_upper:
                return value

        raise AttributeError(
            f"No station or group named '{name}'. Use dir() to see available options."
        )

    def __dir__(self) -> list[str]:
        """Return list of available attributes for autocomplete."""
        return sorted(set(list(self._children.keys()) + list(self._stations.keys())))

    def __repr__(self) -> str:
        """String representation."""
        n_children = len(self._children)
        n_stations = len(self._stations)
        parts = []
        if n_children:
            parts.append(f"{n_children} groups")
        if n_stations:
            parts.append(f"{n_stations} stations")
        return f"<StationNamespace: {', '.join(parts) or 'empty'}>"

    def _ipython_key_completions_(self) -> list[str]:
        """Support bracket completion in IPython."""
        return self.__dir__()


def _fips_to_iso(fips_code: str) -> str:
    """Convert FIPS country code to ISO 3166-1 alpha-2 code.

    Args:
        fips_code: FIPS country code from ISD data

    Returns:
        ISO 3166-1 alpha-2 country code, or original if no mapping exists
    """
    from weathervault._constants import FIPS_TO_ISO

    return FIPS_TO_ISO.get(fips_code, fips_code)


class _StationRegistry(_StationNamespace):
    """Root registry that lazily builds the station hierarchy.

    Stations are organized using ISO 3166-1 alpha-2 country codes:
    - station.<ISO_CODE>.<STATE>.<STATION_NAME> for US stations
    - station.<ISO_CODE>.<STATION_NAME> for other countries

    Examples:
        >>> station.US.NY.LAGUARDIA_AP
        '725030-14732'
        >>> station.DE.BERLIN_TEGEL  # Germany (ISO: DE, FIPS: GM)
        '103820-99999'
    """

    def __init__(self) -> None:
        """Initialize empty registry (loads on first access)."""
        super().__init__()
        self._loaded = False

    def _ensure_loaded(self) -> None:
        """Load station data if not already loaded."""
        if self._loaded:
            return

        df = _get_stations_df()

        # Sort by end_date descending so active stations are processed last
        # (and thus override older stations with the same name)
        df = df.sort("end_date", descending=False, nulls_last=False)

        # Build hierarchy by ISO country code
        country_groups: dict[str, dict[str, dict[str, str] | str]] = {}

        for row in df.iter_rows(named=True):
            station_id = row["id"]
            name = row["name"] or ""
            fips_code = row["country_code"] or "XX"
            # Convert FIPS to ISO for user-facing interface
            country_code = _fips_to_iso(fips_code)
            state = row["state"]

            sanitized_name = _sanitize_name(name)

            if country_code not in country_groups:
                country_groups[country_code] = {}

            # For US stations, add state level
            if country_code == "US" and state:
                if state not in country_groups[country_code]:
                    country_groups[country_code][state] = {}
                state_dict = country_groups[country_code][state]
                if isinstance(state_dict, dict):
                    # Overwrite if same name (newer station replaces older)
                    state_dict[sanitized_name] = station_id
            else:
                # For non-US, put directly under country
                country_groups[country_code][sanitized_name] = station_id

        # Build namespace tree
        for country_code, content in country_groups.items():
            children: dict[str, _StationNamespace] = {}
            stations: dict[str, str] = {}

            for key, value in content.items():
                if isinstance(value, dict):
                    # It's a state with stations
                    children[key] = _StationNamespace(stations=value)
                else:
                    # It's a station directly under country
                    stations[key] = value

            self._children[country_code] = _StationNamespace(stations=stations, children=children)

        self._loaded = True

    def __getattr__(self, name: str) -> _StationNamespace | str:
        """Get a child namespace or station ID, loading data if needed."""
        if name.startswith("_"):
            raise AttributeError(name)
        self._ensure_loaded()
        return super().__getattr__(name)

    def __dir__(self) -> list[str]:
        """Return list of available attributes for autocomplete."""
        self._ensure_loaded()
        return super().__dir__()

    def __repr__(self) -> str:
        """String representation."""
        if not self._loaded:
            return "<StationRegistry: not loaded (access an attribute to load)>"
        return f"<StationRegistry: {len(self._children)} countries>"

    def search(self, pattern: str) -> dict[str, str]:
        """Search for stations matching a pattern.

        Args:
            pattern: Case-insensitive pattern to match against station names

        Returns:
            Dict mapping full paths to station IDs

        Example:
            >>> station.search("laguardia")
            {'US.NY.LAGUARDIA_AP': '725030-14732'}
        """
        self._ensure_loaded()
        results: dict[str, str] = {}
        pattern_upper = pattern.upper()

        for country_code, country_ns in self._children.items():
            # Check stations directly under country
            for name, station_id in country_ns._stations.items():
                if pattern_upper in name.upper():
                    results[f"{country_code}.{name}"] = station_id

            # Check states/children
            for state, state_ns in country_ns._children.items():
                for name, station_id in state_ns._stations.items():
                    if pattern_upper in name.upper():
                        results[f"{country_code}.{state}.{name}"] = station_id

        return results


# Singleton instance
station = _StationRegistry()
