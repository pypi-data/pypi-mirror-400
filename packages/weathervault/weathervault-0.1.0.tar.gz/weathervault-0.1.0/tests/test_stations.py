"""Tests for the stations module."""

import polars as pl
import pytest

import weathervault as wv
from weathervault._constants import COUNTRY_CODES
from weathervault.stations import (
    get_countries,
    get_inventory,
    get_station_metadata,
    get_years_for_station,
    search_stations,
)


class TestGetCountries:
    """Tests for get_countries function."""

    def test_returns_dataframe(self):
        """Test that get_countries returns a DataFrame."""
        result = get_countries()

        assert isinstance(result, pl.DataFrame)
        assert result.height > 0

    def test_has_expected_columns(self):
        """Test that result has expected columns."""
        result = get_countries()

        assert "country_code" in result.columns
        assert "country" in result.columns

    def test_sorted_by_country(self):
        """Test that results are sorted by country name."""
        result = get_countries()

        countries = result["country"].to_list()
        assert countries == sorted(countries)

    def test_contains_known_countries(self):
        """Test that known countries are present."""
        result = get_countries()
        countries = result["country"].to_list()

        assert "United States" in countries
        assert "Canada" in countries
        assert "United Kingdom" in countries


class TestGetStationMetadata:
    """Tests for get_station_metadata function.

    Note: These tests require network access to download station data.
    """

    @pytest.mark.network
    def test_returns_dataframe(self):
        """Test that get_station_metadata returns a DataFrame."""
        result = get_station_metadata()

        assert isinstance(result, pl.DataFrame)
        assert result.height > 0

    @pytest.mark.network
    def test_has_expected_columns(self):
        """Test that result has expected columns."""
        result = get_station_metadata()

        expected_columns = [
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
            "tz_name",
        ]
        for col in expected_columns:
            assert col in result.columns

    @pytest.mark.network
    def test_id_format(self):
        """Test that station IDs are in USAF-WBAN format."""
        result = get_station_metadata()

        # Check first few IDs contain a hyphen
        for station_id in result["id"].head(10).to_list():
            assert "-" in station_id

    @pytest.mark.network
    def test_caching(self):
        """Test that results are cached."""
        result1 = get_station_metadata()
        result2 = get_station_metadata()

        # Should return the same DataFrame object (cached)
        assert result1 is result2

    @pytest.mark.network
    def test_force_refresh(self):
        """Test that force_refresh bypasses cache."""
        result1 = get_station_metadata()
        result2 = get_station_metadata(force_refresh=True)

        # Should return different DataFrame objects
        # (content should be same but different instance)
        assert result1 is not result2
        assert result1.height == result2.height


class TestSearchStations:
    """Tests for search_stations function."""

    @pytest.mark.network
    def test_search_by_state(self):
        """Test searching stations by US state."""
        result = search_stations(state="CA")

        assert isinstance(result, pl.DataFrame)
        # All results should be in California
        assert all(state == "CA" for state in result["state"].to_list() if state)

    @pytest.mark.network
    def test_search_by_country(self):
        """Test searching stations by country name."""
        result = search_stations(country="Canada")

        assert isinstance(result, pl.DataFrame)
        if result.height > 0:
            assert all(code == "CA" for code in result["country_code"].to_list() if code)

    @pytest.mark.network
    def test_search_by_country_code(self):
        """Test searching stations by country code."""
        result = search_stations(country_code="UK")

        assert isinstance(result, pl.DataFrame)
        if result.height > 0:
            assert all(code == "UK" for code in result["country_code"].to_list())

    @pytest.mark.network
    def test_search_by_lat_range(self):
        """Test searching stations by latitude range."""
        result = search_stations(lat_range=(40.0, 41.0))

        assert isinstance(result, pl.DataFrame)
        if result.height > 0:
            lats = result["lat"].to_list()
            assert all(40.0 <= lat <= 41.0 for lat in lats if lat is not None)

    @pytest.mark.network
    def test_search_by_lon_range(self):
        """Test searching stations by longitude range."""
        result = search_stations(lon_range=(-75.0, -74.0))

        assert isinstance(result, pl.DataFrame)
        if result.height > 0:
            lons = result["lon"].to_list()
            assert all(-75.0 <= lon <= -74.0 for lon in lons if lon is not None)

    @pytest.mark.network
    def test_search_by_name(self):
        """Test searching stations by name."""
        result = search_stations(name="airport")

        assert isinstance(result, pl.DataFrame)
        if result.height > 0:
            names = result["name"].to_list()
            assert all("airport" in name.lower() for name in names if name)

    @pytest.mark.network
    def test_combined_search(self):
        """Test searching with multiple criteria."""
        result = search_stations(state="NY", name="airport")

        assert isinstance(result, pl.DataFrame)


class TestGetInventory:
    """Tests for get_inventory function."""

    @pytest.mark.network
    def test_returns_dataframe(self):
        """Test that get_inventory returns a DataFrame."""
        result = get_inventory()

        assert isinstance(result, pl.DataFrame)
        assert result.height > 0

    @pytest.mark.network
    def test_has_expected_columns(self):
        """Test that result has expected columns."""
        result = get_inventory()

        expected_columns = [
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
        for col in expected_columns:
            assert col in result.columns

    @pytest.mark.network
    def test_total_calculated(self):
        """Test that total column is sum of monthly values."""
        result = get_inventory()

        # Check first row
        row = result.row(0, named=True)
        expected_total = sum(
            [
                row["jan"],
                row["feb"],
                row["mar"],
                row["apr"],
                row["may"],
                row["jun"],
                row["jul"],
                row["aug"],
                row["sep"],
                row["oct"],
                row["nov"],
                row["dec"],
            ]
        )
        assert row["total"] == expected_total


class TestGetYearsForStation:
    """Tests for get_years_for_station function."""

    @pytest.mark.network
    def test_returns_list(self):
        """Test that function returns a list."""
        # Use a known station (LaGuardia Airport)
        result = get_years_for_station("725030-14732")

        assert isinstance(result, list)

    @pytest.mark.network
    def test_years_sorted(self):
        """Test that years are sorted."""
        result = get_years_for_station("725030-14732")

        if result:
            assert result == sorted(result)

    @pytest.mark.network
    def test_invalid_station(self):
        """Test that invalid station returns empty list."""
        result = get_years_for_station("000000-00000")

        assert result == []

    @pytest.mark.network
    def test_known_station_has_recent_years(self):
        """Test that a known active station has recent years."""
        result = get_years_for_station("725030-14732")
        # LaGuardia should have data at least from 2020 onwards
        assert any(year >= 2020 for year in result)

    @pytest.mark.network
    def test_known_station_has_historical_years(self):
        """Test that a known station has historical data."""
        result = get_years_for_station("725030-14732")
        # LaGuardia has been recording for decades
        assert any(year < 2000 for year in result)


class TestCountryCodeMapping:
    """Tests for country code mapping in search and metadata."""

    def test_country_codes_dict_not_empty(self):
        """Test that COUNTRY_CODES dictionary is not empty."""
        assert len(COUNTRY_CODES) > 0

    def test_common_fips_codes(self):
        """Test some common FIPS country codes."""
        assert COUNTRY_CODES["US"] == "United States"
        assert COUNTRY_CODES["CA"] == "Canada"
        assert COUNTRY_CODES["UK"] == "United Kingdom"
        assert COUNTRY_CODES["AS"] == "Australia"  # FIPS code for Australia
        assert COUNTRY_CODES["FR"] == "France"

    @pytest.mark.network
    def test_search_by_country_uses_mapping(self):
        """Test that search uses country name to code mapping."""
        # Search by full country name should work
        result = search_stations(country="Australia")
        if result.height > 0:
            # Should find stations with ISO code 'AU' (not FIPS 'AS')
            assert all(code == "AU" for code in result["country_code"].to_list() if code)


class TestSearchStationsAdvanced:
    """Advanced tests for search_stations function."""

    @pytest.mark.network
    def test_empty_result_for_impossible_criteria(self):
        """Test that impossible criteria returns empty DataFrame."""
        # Non-existent country code
        result = search_stations(country_code="ZZ")
        assert result.height == 0

    @pytest.mark.network
    def test_latitude_longitude_combined(self):
        """Test combined latitude and longitude search."""
        # Around New York City
        result = search_stations(lat_range=(40.5, 41.0), lon_range=(-74.5, -73.5))
        assert isinstance(result, pl.DataFrame)
        if result.height > 0:
            # Verify all results are in bounds
            for row in result.iter_rows(named=True):
                if row["lat"] is not None:
                    assert 40.5 <= row["lat"] <= 41.0
                if row["lon"] is not None:
                    assert -74.5 <= row["lon"] <= -73.5

    @pytest.mark.network
    def test_name_search_case_insensitive(self):
        """Test that name search is case insensitive."""
        upper_result = search_stations(name="AIRPORT")
        lower_result = search_stations(name="airport")
        # Both should return results
        assert upper_result.height > 0
        assert lower_result.height > 0

    @pytest.mark.network
    def test_state_combined_with_lat_range(self):
        """Test combining state with latitude range."""
        result = search_stations(state="CA", lat_range=(35.0, 40.0))
        assert isinstance(result, pl.DataFrame)
        if result.height > 0:
            # All should be in California and within lat range
            for row in result.iter_rows(named=True):
                if row["state"]:
                    assert row["state"] == "CA"
                if row["lat"] is not None:
                    assert 35.0 <= row["lat"] <= 40.0


class TestStationMetadataDetails:
    """Detailed tests for station metadata quality."""

    @pytest.mark.network
    def test_timezone_populated(self):
        """Test that timezone is populated for stations with coordinates."""
        result = get_station_metadata()
        # Stations with lat/lon should have timezone
        with_coords = result.filter(pl.col("lat").is_not_null() & pl.col("lon").is_not_null())
        if with_coords.height > 0:
            # At least some should have timezone
            tz_populated = with_coords.filter(pl.col("tz_name").is_not_null()).height
            assert tz_populated > 0

    @pytest.mark.network
    def test_station_dates_valid(self):
        """Test that begin_date and end_date are valid dates."""
        result = get_station_metadata()
        # Check that dates are not null for at least some stations
        with_dates = result.filter(pl.col("begin_date").is_not_null())
        assert with_dates.height > 0

    @pytest.mark.network
    def test_elevation_reasonable(self):
        """Test that elevations are in reasonable range."""
        result = get_station_metadata()
        elevations = result.filter(pl.col("elev").is_not_null())["elev"].to_list()
        # Elevations should be between -500m (Dead Sea area) and 10000m (extreme mountains)
        # Missing values (-999.0, -999.9) should already be converted to null
        out_of_range = [elev for elev in elevations if not (-500 < elev < 10000)]
        assert len(out_of_range) == 0, (
            f"Found {len(out_of_range)} elevations out of range [-500, 10000]: "
            f"min={min(out_of_range) if out_of_range else 'N/A'}, "
            f"max={max(out_of_range) if out_of_range else 'N/A'}"
        )


class TestInventoryDetails:
    """Detailed tests for inventory data."""

    @pytest.mark.network
    def test_monthly_values_non_negative(self):
        """Test that monthly observation counts are non-negative."""
        result = get_inventory()
        months = [
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
        ]
        for month in months:
            assert all(v >= 0 for v in result[month].to_list())

    @pytest.mark.network
    def test_years_reasonable(self):
        """Test that years in inventory are reasonable."""
        result = get_inventory()
        years = result["year"].unique().to_list()
        # Should have years from historical to recent
        assert min(years) < 2000  # Has historical data
        assert max(years) >= 2020  # Has recent data

    @pytest.mark.network
    def test_inventory_matches_station_format(self):
        """Test that inventory IDs match station ID format."""
        result = get_inventory()
        # All IDs should contain hyphen
        assert all("-" in sid for sid in result["id"].to_list())


class TestCountryShorthand:
    """Tests for the country code shorthand (wv.country.XX)."""

    def test_country_exists(self):
        """Test that wv.country exists."""
        assert hasattr(wv, "country")

    def test_returns_uppercase_code(self):
        """Test that country codes are returned in uppercase."""
        assert wv.country.US == "US"
        assert wv.country.GB == "GB"
        assert wv.country.DE == "DE"
        assert wv.country.FR == "FR"

    def test_lowercase_access_works(self):
        """Test that lowercase attribute access works."""
        assert wv.country.us == "US"
        assert wv.country.gb == "GB"
        assert wv.country.de == "DE"

    def test_invalid_code_raises_error(self):
        """Test that invalid country codes raise AttributeError."""
        with pytest.raises(AttributeError, match="not a valid ISO 3166-1 alpha-2"):
            _ = wv.country.INVALID

    @pytest.mark.network
    def test_works_in_search_stations(self):
        """Test that country shorthand works in search_stations."""
        # Should work just like passing string "US"
        result1 = search_stations(country_code=wv.country.US)
        result2 = search_stations(country_code="US")

        assert result1.height == result2.height
        assert result1.height > 0

    @pytest.mark.network
    def test_multiple_countries(self):
        """Test using country shorthand for multiple countries."""
        de = search_stations(country_code=wv.country.DE)
        gb = search_stations(country_code=wv.country.GB)
        fr = search_stations(country_code=wv.country.FR)

        assert de.height > 0
        assert gb.height > 0
        assert fr.height > 0

        # Verify they return different results
        assert de.height != gb.height
        assert de.height != fr.height

    def test_dir_returns_country_codes(self):
        """Test that dir() returns list of country codes."""
        codes = dir(wv.country)

        # Should contain known ISO codes
        assert "US" in codes
        assert "GB" in codes
        assert "DE" in codes
        assert "FR" in codes
        assert len(codes) > 200  # Should have many country codes

    def test_repr(self):
        """Test string representation of country object."""
        repr_str = repr(wv.country)
        assert "CountryCodes" in repr_str
        assert "ISO 3166-1" in repr_str


class TestStateShorthand:
    """Tests for the US state code shorthand (wv.state.XX)."""

    def test_state_exists(self):
        """Test that wv.state exists."""
        assert hasattr(wv, "state")

    def test_returns_uppercase_code(self):
        """Test that state codes are returned in uppercase."""
        assert wv.state.CA == "CA"
        assert wv.state.NY == "NY"
        assert wv.state.TX == "TX"
        assert wv.state.FL == "FL"

    def test_lowercase_access_works(self):
        """Test that lowercase attribute access works."""
        assert wv.state.ca == "CA"
        assert wv.state.ny == "NY"
        assert wv.state.tx == "TX"

    def test_territories_included(self):
        """Test that US territories are included."""
        assert wv.state.PR == "PR"  # Puerto Rico
        assert wv.state.GU == "GU"  # Guam
        assert wv.state.VI == "VI"  # U.S. Virgin Islands
        assert wv.state.AS == "AS"  # American Samoa
        assert wv.state.MP == "MP"  # Northern Mariana Islands
        assert wv.state.DC == "DC"  # District of Columbia

    def test_invalid_code_raises_error(self):
        """Test that invalid state codes raise AttributeError."""
        with pytest.raises(AttributeError, match="not a valid US state"):
            _ = wv.state.INVALID

    @pytest.mark.network
    def test_works_in_search_stations(self):
        """Test that state shorthand works in search_stations."""
        # Should work just like passing string "CA"
        result1 = search_stations(state=wv.state.CA)
        result2 = search_stations(state="CA")

        assert result1.height == result2.height
        assert result1.height > 0

    @pytest.mark.network
    def test_multiple_states(self):
        """Test using state shorthand for multiple states."""
        ca = search_stations(state=wv.state.CA)
        ny = search_stations(state=wv.state.NY)
        tx = search_stations(state=wv.state.TX)

        assert ca.height > 0
        assert ny.height > 0
        assert tx.height > 0

        # Verify they return different results
        assert ca.height != ny.height
        assert ca.height != tx.height

    def test_dir_returns_state_codes(self):
        """Test that dir() returns list of state codes."""
        codes = dir(wv.state)

        # Should contain known state codes
        assert "CA" in codes
        assert "NY" in codes
        assert "TX" in codes
        assert "FL" in codes
        assert len(codes) == 56  # 50 states + DC + 5 territories

    def test_repr(self):
        """Test string representation of state object."""
        repr_str = repr(wv.state)
        assert "StateCodes" in repr_str
        assert "US states" in repr_str
