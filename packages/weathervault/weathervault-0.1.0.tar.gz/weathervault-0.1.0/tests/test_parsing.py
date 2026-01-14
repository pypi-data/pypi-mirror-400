"""Tests for the parsing module."""

import polars as pl
import pytest

from weathervault._constants import MANDATORY_COLUMN_NAMES
from weathervault._parsing import (
    _empty_processed_dataframe,
    _empty_weather_dataframe,
    parse_isd_data,
    parse_isd_line,
    process_weather_data,
)


class TestParseIsdLine:
    """Tests for parse_isd_line function."""

    def test_parse_valid_line(self):
        """Test parsing a valid ISD line."""
        # Example ISD line (105 characters for mandatory section)
        # Build the line according to exact column widths:
        # 4+6+5+4+2+2+2+2+1+6+7+5+5+5+4+3+1+1+4+1+5+1+1+1+6+1+1+1+5+1+5+1+5+1 = 105
        line = (
            "0105"  # Total variable length (4)
            "725030"  # USAF (6)
            "14732"  # WBAN (5)
            "2023"  # Year (4)
            "07"  # Month (2)
            "15"  # Day (2)
            "14"  # Hour (2)
            "00"  # Minute (2)
            "4"  # Data source (1)
            "+40750"  # Latitude (6)
            "-073900"  # Longitude (7)
            "FM-15"  # Report type (5)
            "+0003"  # Elevation (5)
            "KLGA "  # Call letters (5 with padding)
            "V020"  # QC process (4)
            "270"  # Wind direction (3)
            "1"  # Wind direction QC (1)
            "N"  # Wind type (1)
            "0051"  # Wind speed (4)
            "1"  # Wind speed QC (1)
            "22000"  # Ceiling height (5)
            "1"  # Ceiling height QC (1)
            "9"  # Ceiling determination (1)
            "N"  # CAVOK (1)
            "016093"  # Visibility (6)
            "1"  # Visibility QC (1)
            "N"  # Visibility variability (1)
            "9"  # Visibility variability QC (1)
            "+0261"  # Temperature (5)
            "1"  # Temperature QC (1)
            "+0172"  # Dew point (5)
            "1"  # Dew point QC (1)
            "10132"  # Sea level pressure (5)
            "1"  # Sea level pressure QC (1)
        )

        result = parse_isd_line(line)

        assert result["usaf"] == "725030"
        assert result["wban"] == "14732"
        assert result["year"] == "2023"
        assert result["month"] == "07"
        assert result["day"] == "15"
        assert result["hour"] == "14"
        assert result["minute"] == "00"
        assert result["wind_direction"] == "270"
        assert result["wind_speed"] == "0051"
        assert result["temp"] == "+0261"
        assert result["dew_point"] == "+0172"

    def test_parse_short_line(self):
        """Test parsing a line shorter than expected."""
        short_line = "0105725030147322023"
        result = parse_isd_line(short_line)

        # First few fields should be parsed
        assert result["total_chars"] == "0105"
        assert result["usaf"] == "725030"
        # Later fields should be None
        assert result["temp"] is None

    def test_parse_empty_fields(self):
        """Test that empty fields are returned as None."""
        # Line with some empty/whitespace fields
        line = "0105" + " " * 101  # Padded with spaces
        result = parse_isd_line(line)

        # Empty fields should be None
        assert result["usaf"] is None


class TestParseIsdData:
    """Tests for parse_isd_data function."""

    def test_parse_multiple_lines(self):
        """Test parsing multiple lines of ISD data."""
        # Create sample data with two observations
        line1 = (
            "0105725030147322023071514004+40750-073900FM-15+0003KLGA V020"
            "2701N00511220001N9N01609319N+02611+01721101321"
        )
        line2 = (
            "0105725030147322023071515004+40750-073900FM-15+0003KLGA V020"
            "2801N00521220001N9N01609319N+02711+01821101301"
        )
        data = f"{line1}\n{line2}"

        result = parse_isd_data(data)

        assert isinstance(result, pl.DataFrame)
        assert result.height == 2
        assert "usaf" in result.columns

    def test_parse_empty_data(self):
        """Test parsing empty data returns empty DataFrame."""
        result = parse_isd_data("")

        assert isinstance(result, pl.DataFrame)
        assert result.height == 0

    def test_parse_bytes_data(self):
        """Test parsing bytes data."""
        line = (
            "0105725030147322023071514004+40750-073900FM-15+0003KLGA V020"
            "2701N00511220001N9N01609319N+02611+01721101321"
        )
        data = line.encode("utf-8")

        result = parse_isd_data(data)

        assert isinstance(result, pl.DataFrame)
        assert result.height == 1


class TestProcessWeatherData:
    """Tests for process_weather_data function."""

    def test_process_empty_dataframe(self):
        """Test processing an empty DataFrame."""
        empty_df = _empty_weather_dataframe()
        result = process_weather_data(empty_df)

        assert isinstance(result, pl.DataFrame)
        assert result.height == 0

    def test_temperature_conversion(self):
        """Test that temperature values are scaled correctly."""
        # Create a minimal DataFrame with temperature data
        df = pl.DataFrame(
            {
                "usaf": ["725030"],
                "wban": ["14732"],
                "year": ["2023"],
                "month": ["07"],
                "day": ["15"],
                "hour": ["14"],
                "minute": ["00"],
                "wind_direction": ["270"],
                "wind_speed": ["0051"],
                "ceiling_height": ["22000"],
                "visibility": ["016093"],
                "temp": ["+0261"],  # 26.1°C
                "dew_point": ["+0172"],  # 17.2°C
                "sea_level_pressure": ["10132"],  # 1013.2 hPa
                # Fill in other required columns with defaults
                "total_chars": ["0105"],
                "data_source": ["4"],
                "latitude": ["+40750"],
                "longitude": ["-073900"],
                "report_type": ["FM-15"],
                "elevation": ["+0003"],
                "call_letters": ["KLGA"],
                "qc_process": ["V020"],
                "wind_direction_qc": ["1"],
                "wind_type": ["N"],
                "wind_speed_qc": ["1"],
                "ceiling_height_qc": ["1"],
                "ceiling_determination": ["9"],
                "cavok": ["N"],
                "visibility_qc": ["1"],
                "visibility_variability": ["N"],
                "visibility_variability_qc": ["9"],
                "temp_qc": ["1"],
                "dew_point_qc": ["1"],
                "sea_level_pressure_qc": ["1"],
            }
        )

        result = process_weather_data(df, temp_unit="celsius")

        assert result["temp"][0] == pytest.approx(26.1, rel=0.01)
        assert result["dew_point"][0] == pytest.approx(17.2, rel=0.01)

    def test_fahrenheit_conversion(self):
        """Test temperature conversion to Fahrenheit."""
        df = pl.DataFrame(
            {
                "usaf": ["725030"],
                "wban": ["14732"],
                "year": ["2023"],
                "month": ["07"],
                "day": ["15"],
                "hour": ["14"],
                "minute": ["00"],
                "wind_direction": ["270"],
                "wind_speed": ["0051"],
                "ceiling_height": ["22000"],
                "visibility": ["016093"],
                "temp": ["+0261"],  # 26.1°C = 79.0°F
                "dew_point": ["+0172"],  # 17.2°C = 63.0°F
                "sea_level_pressure": ["10132"],
                "total_chars": ["0105"],
                "data_source": ["4"],
                "latitude": ["+40750"],
                "longitude": ["-073900"],
                "report_type": ["FM-15"],
                "elevation": ["+0003"],
                "call_letters": ["KLGA"],
                "qc_process": ["V020"],
                "wind_direction_qc": ["1"],
                "wind_type": ["N"],
                "wind_speed_qc": ["1"],
                "ceiling_height_qc": ["1"],
                "ceiling_determination": ["9"],
                "cavok": ["N"],
                "visibility_qc": ["1"],
                "visibility_variability": ["N"],
                "visibility_variability_qc": ["9"],
                "temp_qc": ["1"],
                "dew_point_qc": ["1"],
                "sea_level_pressure_qc": ["1"],
            }
        )

        result = process_weather_data(df, temp_unit="fahrenheit")

        # 26.1°C = 78.98°F
        assert result["temp"][0] == pytest.approx(79.0, rel=0.1)

    def test_missing_values_converted_to_null(self):
        """Test that missing value codes are converted to null."""
        df = pl.DataFrame(
            {
                "usaf": ["725030"],
                "wban": ["14732"],
                "year": ["2023"],
                "month": ["07"],
                "day": ["15"],
                "hour": ["14"],
                "minute": ["00"],
                "wind_direction": ["999"],  # Missing value
                "wind_speed": ["9999"],  # Missing value
                "ceiling_height": ["99999"],  # Missing value
                "visibility": ["999999"],  # Missing value
                "temp": ["+9999"],  # Missing value
                "dew_point": ["+9999"],  # Missing value
                "sea_level_pressure": ["99999"],  # Missing value
                "total_chars": ["0105"],
                "data_source": ["4"],
                "latitude": ["+40750"],
                "longitude": ["-073900"],
                "report_type": ["FM-15"],
                "elevation": ["+0003"],
                "call_letters": ["KLGA"],
                "qc_process": ["V020"],
                "wind_direction_qc": ["9"],
                "wind_type": ["9"],
                "wind_speed_qc": ["9"],
                "ceiling_height_qc": ["9"],
                "ceiling_determination": ["9"],
                "cavok": ["N"],
                "visibility_qc": ["9"],
                "visibility_variability": ["N"],
                "visibility_variability_qc": ["9"],
                "temp_qc": ["9"],
                "dew_point_qc": ["9"],
                "sea_level_pressure_qc": ["9"],
            }
        )

        result = process_weather_data(df)

        assert result["wd"][0] is None
        assert result["ws"][0] is None
        assert result["ceil_hgt"][0] is None
        assert result["visibility"][0] is None
        assert result["temp"][0] is None
        assert result["dew_point"][0] is None
        assert result["atmos_pres"][0] is None

    def test_wind_speed_scaling(self):
        """Test that wind speed is scaled correctly (divide by 10)."""
        df = pl.DataFrame(
            {
                "usaf": ["725030"],
                "wban": ["14732"],
                "year": ["2023"],
                "month": ["07"],
                "day": ["15"],
                "hour": ["14"],
                "minute": ["00"],
                "wind_direction": ["270"],
                "wind_speed": ["0051"],  # 5.1 m/s
                "ceiling_height": ["22000"],
                "visibility": ["016093"],
                "temp": ["+0261"],
                "dew_point": ["+0172"],
                "sea_level_pressure": ["10132"],
                "total_chars": ["0105"],
                "data_source": ["4"],
                "latitude": ["+40750"],
                "longitude": ["-073900"],
                "report_type": ["FM-15"],
                "elevation": ["+0003"],
                "call_letters": ["KLGA"],
                "qc_process": ["V020"],
                "wind_direction_qc": ["1"],
                "wind_type": ["N"],
                "wind_speed_qc": ["1"],
                "ceiling_height_qc": ["1"],
                "ceiling_determination": ["9"],
                "cavok": ["N"],
                "visibility_qc": ["1"],
                "visibility_variability": ["N"],
                "visibility_variability_qc": ["9"],
                "temp_qc": ["1"],
                "dew_point_qc": ["1"],
                "sea_level_pressure_qc": ["1"],
            }
        )

        result = process_weather_data(df)

        assert result["ws"][0] == pytest.approx(5.1, rel=0.01)


class TestEmptyDataFrames:
    """Tests for empty DataFrame creation functions."""

    def test_empty_weather_dataframe(self):
        """Test empty weather DataFrame has correct schema."""
        df = _empty_weather_dataframe()

        assert isinstance(df, pl.DataFrame)
        assert df.height == 0
        assert "usaf" in df.columns
        assert "temp" in df.columns

    def test_empty_weather_dataframe_has_all_columns(self):
        """Test empty weather DataFrame has all mandatory columns."""
        df = _empty_weather_dataframe()
        for col in MANDATORY_COLUMN_NAMES:
            assert col in df.columns

    def test_empty_processed_dataframe(self):
        """Test empty processed DataFrame has correct schema."""
        df = _empty_processed_dataframe()

        assert isinstance(df, pl.DataFrame)
        assert df.height == 0
        assert "id" in df.columns
        assert "time" in df.columns
        assert "temp" in df.columns
        assert "rh" in df.columns
        assert "wd" in df.columns
        assert "ws" in df.columns

    def test_empty_processed_dataframe_columns(self):
        """Test empty processed DataFrame has exactly expected columns."""
        df = _empty_processed_dataframe()
        expected_columns = [
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
        assert df.columns == expected_columns

    def test_empty_processed_dataframe_dtypes(self):
        """Test empty processed DataFrame has correct data types."""
        df = _empty_processed_dataframe()
        assert df.schema["id"] == pl.Utf8
        assert df.schema["temp"] == pl.Float64
        assert df.schema["wd"] == pl.Int32
        assert df.schema["ws"] == pl.Float64


class TestRelativeHumidityCalculation:
    """Tests for relative humidity calculation."""

    def test_rh_calculation_hot_humid(self):
        """Test RH calculation for hot humid conditions."""
        df = _create_test_dataframe(temp="+0300", dew_point="+0250")  # 30°C, 25°C dew point
        result = process_weather_data(df)
        # At 30°C with 25°C dew point, RH should be around 75%
        assert 70 < result["rh"][0] < 80

    def test_rh_calculation_cold_dry(self):
        """Test RH calculation for cold dry conditions."""
        df = _create_test_dataframe(temp="-0100", dew_point="-0150")  # -10°C, -15°C dew point
        result = process_weather_data(df)
        # Should have lower relative humidity
        assert 50 < result["rh"][0] < 80

    def test_rh_calculation_saturated(self):
        """Test RH calculation when temp equals dew point (100% RH)."""
        df = _create_test_dataframe(temp="+0200", dew_point="+0200")  # Same temp and dew point
        result = process_weather_data(df)
        # Should be 100% (or very close)
        assert result["rh"][0] == pytest.approx(100.0, rel=0.01)


class TestNegativeTemperatures:
    """Tests for handling negative temperatures."""

    def test_negative_temperature_parsing(self):
        """Test that negative temperatures are parsed correctly."""
        df = _create_test_dataframe(temp="-0150", dew_point="-0200")  # -15°C, -20°C
        result = process_weather_data(df)
        assert result["temp"][0] == pytest.approx(-15.0, rel=0.01)
        assert result["dew_point"][0] == pytest.approx(-20.0, rel=0.01)

    def test_negative_temperature_fahrenheit(self):
        """Test negative temperature conversion to Fahrenheit."""
        df = _create_test_dataframe(temp="-0100", dew_point="-0150")  # -10°C
        result = process_weather_data(df, temp_unit="fahrenheit")
        # -10°C = 14°F
        assert result["temp"][0] == pytest.approx(14.0, rel=0.1)


class TestEdgeCases:
    """Tests for edge cases in parsing."""

    def test_whitespace_only_line(self):
        """Test parsing a line with only whitespace."""
        result = parse_isd_line("   \t\n")
        assert result["usaf"] is None

    def test_partial_line(self):
        """Test parsing a partial line."""
        # Just the first few fields
        line = "0105725030"
        result = parse_isd_line(line)
        assert result["total_chars"] == "0105"
        assert result["usaf"] == "725030"
        assert result["wban"] is None

    def test_line_with_additional_data(self):
        """Test that additional data section is ignored in mandatory parsing."""
        # 105 char mandatory section + extra data
        mandatory = (
            "0150"
            "725030"
            "14732"
            "2023"
            "07"
            "15"
            "14"
            "00"
            "4"
            "+40750"
            "-073900"
            "FM-15"
            "+0003"
            "KLGA "
            "V020"
            "270"
            "1"
            "N"
            "0051"
            "1"
            "22000"
            "1"
            "9"
            "N"
            "016093"
            "1"
            "N"
            "9"
            "+0261"
            "1"
            "+0172"
            "1"
            "10132"
            "1"
        )
        additional = "ADD1EXTRA_DATA_HERE"
        line = mandatory + additional

        result = parse_isd_line(line)
        # Should still parse mandatory section correctly
        assert result["usaf"] == "725030"
        assert result["temp"] == "+0261"


def _create_test_dataframe(
    temp: str = "+0261",
    dew_point: str = "+0172",
    wind_direction: str = "270",
    wind_speed: str = "0051",
) -> pl.DataFrame:
    """Helper function to create a test DataFrame with weather data."""
    return pl.DataFrame(
        {
            "usaf": ["725030"],
            "wban": ["14732"],
            "year": ["2023"],
            "month": ["07"],
            "day": ["15"],
            "hour": ["14"],
            "minute": ["00"],
            "wind_direction": [wind_direction],
            "wind_speed": [wind_speed],
            "ceiling_height": ["22000"],
            "visibility": ["016093"],
            "temp": [temp],
            "dew_point": [dew_point],
            "sea_level_pressure": ["10132"],
            "total_chars": ["0105"],
            "data_source": ["4"],
            "latitude": ["+40750"],
            "longitude": ["-073900"],
            "report_type": ["FM-15"],
            "elevation": ["+0003"],
            "call_letters": ["KLGA"],
            "qc_process": ["V020"],
            "wind_direction_qc": ["1"],
            "wind_type": ["N"],
            "wind_speed_qc": ["1"],
            "ceiling_height_qc": ["1"],
            "ceiling_determination": ["9"],
            "cavok": ["N"],
            "visibility_qc": ["1"],
            "visibility_variability": ["N"],
            "visibility_variability_qc": ["9"],
            "temp_qc": ["1"],
            "dew_point_qc": ["1"],
            "sea_level_pressure_qc": ["1"],
        }
    )
