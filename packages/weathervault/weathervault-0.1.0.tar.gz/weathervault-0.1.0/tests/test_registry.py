"""Tests for the station registry module."""

import pytest

import weathervault as wv
from weathervault._registry import _sanitize_name, _StationNamespace, station


class TestSanitizeName:
    """Tests for the _sanitize_name function."""

    def test_basic_name(self):
        """Test simple station name."""
        assert _sanitize_name("LAGUARDIA") == "LAGUARDIA"

    def test_name_with_spaces(self):
        """Test name with spaces becomes underscores."""
        assert _sanitize_name("LA GUARDIA AIRPORT") == "LA_GUARDIA_AIRPORT"

    def test_name_with_special_chars(self):
        """Test special characters are replaced."""
        assert _sanitize_name("ST. LOUIS") == "ST_LOUIS"
        assert _sanitize_name("JOHN F. KENNEDY") == "JOHN_F_KENNEDY"

    def test_name_starting_with_number(self):
        """Test names starting with numbers get underscore prefix."""
        assert _sanitize_name("1ST STREET") == "_1ST_STREET"

    def test_empty_name(self):
        """Test empty name returns UNKNOWN."""
        assert _sanitize_name("") == "UNKNOWN"
        assert _sanitize_name(None) == "UNKNOWN"

    def test_lowercase_converted(self):
        """Test lowercase is converted to uppercase."""
        assert _sanitize_name("new york") == "NEW_YORK"


class TestStationNamespace:
    """Tests for the _StationNamespace class."""

    def test_access_station(self):
        """Test accessing a station returns its ID."""
        ns = _StationNamespace(stations={"TEST_STATION": "123456-99999"})
        assert ns.TEST_STATION == "123456-99999"

    def test_access_child_namespace(self):
        """Test accessing a child namespace."""
        child = _StationNamespace(stations={"CHILD_STATION": "111111-99999"})
        ns = _StationNamespace(children={"CHILD": child})
        assert child == ns.CHILD
        assert ns.CHILD.CHILD_STATION == "111111-99999"

    def test_dir_returns_available_names(self):
        """Test dir() returns station and child names."""
        child = _StationNamespace()
        ns = _StationNamespace(
            stations={"STATION_A": "1", "STATION_B": "2"},
            children={"GROUP_X": child},
        )
        names = dir(ns)
        assert "STATION_A" in names
        assert "STATION_B" in names
        assert "GROUP_X" in names

    def test_attribute_error_for_unknown(self):
        """Test AttributeError for unknown station."""
        ns = _StationNamespace(stations={"KNOWN": "123"})
        with pytest.raises(AttributeError):
            _ = ns.UNKNOWN

    def test_case_insensitive_access(self):
        """Test case-insensitive attribute access."""
        ns = _StationNamespace(stations={"TEST_STATION": "123456-99999"})
        assert ns.test_station == "123456-99999"


class TestStationRegistry:
    """Tests for the station registry singleton."""

    def test_registry_exists(self):
        """Test that station registry is exported."""
        assert hasattr(wv, "station")
        assert wv.station is station

    def test_registry_repr_before_load(self):
        """Test repr shows not loaded initially."""
        # Create a fresh registry for this test
        from weathervault._registry import _StationRegistry

        fresh = _StationRegistry()
        assert "not loaded" in repr(fresh)

    @pytest.mark.network
    def test_access_us_namespace(self):
        """Test accessing US namespace loads data."""
        us = wv.station.US
        assert isinstance(us, _StationNamespace)

    @pytest.mark.network
    def test_access_us_state(self):
        """Test accessing a US state."""
        ny = wv.station.US.NY
        assert isinstance(ny, _StationNamespace)
        # Should have stations
        assert len(dir(ny)) > 0

    @pytest.mark.network
    def test_get_known_station_id(self):
        """Test getting a known station ID."""
        # JFK airport should be available
        jfk_id = wv.station.US.NY.JOHN_F_KENNEDY_INTERNATIONAL_AIRPORT
        assert jfk_id == "744860-94789"

    @pytest.mark.network
    def test_search_functionality(self):
        """Test the search method."""
        results = wv.station.search("kennedy")
        assert len(results) > 0
        # Should find JFK
        assert any("KENNEDY" in key for key in results)

    @pytest.mark.network
    def test_active_station_preferred(self):
        """Test that active stations are preferred over historical ones."""
        # LA GUARDIA AIRPORT (725030-14732) should be preferred over
        # NEW YORK LAGUARDIA ARPT (999999-14732) which ended in 1972
        lga_id = wv.station.US.NY.LA_GUARDIA_AIRPORT
        assert lga_id == "725030-14732"

    @pytest.mark.network
    def test_non_us_country(self):
        """Test accessing non-US countries."""
        # Germany should have stations (ISO code DE, FIPS code GM)
        de = wv.station.DE  # Germany uses ISO code DE
        assert hasattr(de, "__getattr__")  # Should be a country node

    @pytest.mark.network
    def test_use_with_get_weather_data(self):
        """Test that station IDs work with get_weather_data."""
        station_id = wv.station.US.NY.JOHN_F_KENNEDY_INTERNATIONAL_AIRPORT
        # Just verify it's a valid string format
        assert isinstance(station_id, str)
        assert "-" in station_id
        parts = station_id.split("-")
        assert len(parts) == 2
        assert parts[0].isdigit()
        assert parts[1].isdigit()
