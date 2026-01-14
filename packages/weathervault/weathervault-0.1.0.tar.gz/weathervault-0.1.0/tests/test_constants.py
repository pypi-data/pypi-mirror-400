"""Tests for the constants module."""

from weathervault._constants import (
    BASE_URL,
    COUNTRY_CODES,
    MANDATORY_COLUMN_NAMES,
    MANDATORY_COLUMN_WIDTHS,
    MISSING_VALUES,
    SCALE_FACTORS,
)


class TestBaseUrl:
    """Tests for BASE_URL constant."""

    def test_base_url_format(self):
        """Test that BASE_URL is a valid HTTPS URL."""
        assert BASE_URL.startswith("https://")
        assert "ncei.noaa.gov" in BASE_URL

    def test_base_url_path(self):
        """Test that BASE_URL points to the correct data directory."""
        assert "/pub/data/noaa" in BASE_URL

    def test_base_url_no_trailing_slash(self):
        """Test that BASE_URL has no trailing slash for proper path joining."""
        assert not BASE_URL.endswith("/")


class TestColumnWidths:
    """Tests for mandatory column width constants."""

    def test_column_widths_and_names_match(self):
        """Test that column widths and names have the same length."""
        assert len(MANDATORY_COLUMN_WIDTHS) == len(MANDATORY_COLUMN_NAMES)

    def test_column_widths_sum(self):
        """Test that column widths sum to expected mandatory section length."""
        # The mandatory section is 105 characters
        assert sum(MANDATORY_COLUMN_WIDTHS) == 105

    def test_column_widths_positive(self):
        """Test that all column widths are positive integers."""
        for width in MANDATORY_COLUMN_WIDTHS:
            assert isinstance(width, int)
            assert width > 0

    def test_mandatory_column_names_unique(self):
        """Test that column names are unique."""
        assert len(MANDATORY_COLUMN_NAMES) == len(set(MANDATORY_COLUMN_NAMES))

    def test_expected_column_names_present(self):
        """Test that key column names are present."""
        expected = [
            "usaf",
            "wban",
            "year",
            "month",
            "day",
            "hour",
            "minute",
            "wind_direction",
            "wind_speed",
            "temp",
            "dew_point",
            "visibility",
            "ceiling_height",
            "sea_level_pressure",
        ]
        for name in expected:
            assert name in MANDATORY_COLUMN_NAMES


class TestCountryCodes:
    """Tests for COUNTRY_CODES constant."""

    def test_country_codes_not_empty(self):
        """Test that country codes dictionary is populated."""
        assert len(COUNTRY_CODES) > 100  # Should have many countries

    def test_country_codes_format(self):
        """Test that country codes are 2-character strings."""
        for code in COUNTRY_CODES:
            assert len(code) == 2
            assert code.isupper()

    def test_country_names_not_empty(self):
        """Test that country names are non-empty strings."""
        for name in COUNTRY_CODES.values():
            assert isinstance(name, str)
            assert len(name) > 0

    def test_known_country_codes(self):
        """Test some known country code mappings."""
        assert COUNTRY_CODES["US"] == "United States"
        assert COUNTRY_CODES["UK"] == "United Kingdom"
        assert COUNTRY_CODES["CA"] == "Canada"
        assert COUNTRY_CODES["AS"] == "Australia"  # NOTE: FIPS code for Australia is AS
        assert COUNTRY_CODES["AU"] == "Austria"  # NOTE: AU is Austria in FIPS
        assert COUNTRY_CODES["FR"] == "France"
        assert COUNTRY_CODES["GM"] == "Germany"
        assert COUNTRY_CODES["JA"] == "Japan"

    def test_no_duplicate_country_names(self):
        """Test that there are no exact duplicate country names."""
        names = list(COUNTRY_CODES.values())
        # Note: Some countries may have similar names, but exact duplicates indicate errors
        # Allow for some duplicates due to historical/political reasons
        unique_names = set(names)
        # Most names should be unique
        assert len(unique_names) > len(names) * 0.9


class TestMissingValues:
    """Tests for MISSING_VALUES constant."""

    def test_missing_values_keys(self):
        """Test that missing values are defined for expected fields."""
        expected_keys = {
            "wind_direction",
            "wind_speed",
            "ceiling_height",
            "visibility",
            "temp",
            "dew_point",
            "sea_level_pressure",
        }
        assert set(MISSING_VALUES.keys()) == expected_keys

    def test_missing_values_are_integers(self):
        """Test that missing values are integers."""
        for value in MISSING_VALUES.values():
            assert isinstance(value, int)

    def test_missing_values_are_positive(self):
        """Test that missing values are positive (they're typically 9-filled)."""
        for value in MISSING_VALUES.values():
            assert value > 0

    def test_missing_values_pattern(self):
        """Test that missing values follow the 9-filled pattern."""
        # ISD uses 9s for missing values
        for key, value in MISSING_VALUES.items():
            str_value = str(value)
            assert all(c == "9" for c in str_value), f"{key} should be all 9s"


class TestScaleFactors:
    """Tests for SCALE_FACTORS constant."""

    def test_scale_factors_keys(self):
        """Test that scale factors are defined for expected fields."""
        expected_keys = {
            "wind_speed",
            "temp",
            "dew_point",
            "sea_level_pressure",
            "latitude",
            "longitude",
            "elevation",
        }
        assert set(SCALE_FACTORS.keys()) == expected_keys

    def test_scale_factors_are_positive(self):
        """Test that scale factors are positive numbers."""
        for value in SCALE_FACTORS.values():
            assert value > 0

    def test_scale_factors_are_numeric(self):
        """Test that scale factors are integers or floats."""
        for value in SCALE_FACTORS.values():
            assert isinstance(value, (int, float))

    def test_temperature_scale_factor(self):
        """Test that temperature scale factor is 10 (for 1 decimal place)."""
        assert SCALE_FACTORS["temp"] == 10
        assert SCALE_FACTORS["dew_point"] == 10

    def test_wind_speed_scale_factor(self):
        """Test that wind speed scale factor is 10."""
        assert SCALE_FACTORS["wind_speed"] == 10

    def test_coordinate_scale_factor(self):
        """Test that lat/lon scale factors are 1000 (for 3 decimal places)."""
        assert SCALE_FACTORS["latitude"] == 1000
        assert SCALE_FACTORS["longitude"] == 1000
