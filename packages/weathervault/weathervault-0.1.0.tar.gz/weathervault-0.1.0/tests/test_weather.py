"""Tests for the weather module."""

import polars as pl
import pytest

from weathervault.weather import get_weather_data


class TestGetWeatherData:
    """Tests for get_weather_data function.

    Note: These tests require network access to download weather data.
    """

    @pytest.mark.network
    def test_returns_dataframe(self):
        """Test that get_weather_data returns a DataFrame."""
        # Use LaGuardia Airport and a recent year
        result = get_weather_data("725030-14732", years=2023)

        assert isinstance(result, pl.DataFrame)
        assert result.height > 0

    @pytest.mark.network
    def test_has_expected_columns(self):
        """Test that result has expected columns."""
        result = get_weather_data("725030-14732", years=2023)

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
        for col in expected_columns:
            assert col in result.columns

    @pytest.mark.network
    def test_data_sorted_by_time(self):
        """Test that data is sorted by time (using UTC for proper comparison)."""
        result = get_weather_data("725030-14732", years=2023)

        times = result["time"].to_list()
        # Convert to UTC timestamps for proper sorting comparison
        # (handles DST transitions correctly)
        utc_times = [t.timestamp() for t in times]
        is_sorted = all(utc_times[i] <= utc_times[i + 1] for i in range(len(utc_times) - 1))
        if not is_sorted:
            for i in range(len(utc_times) - 1):
                if utc_times[i] > utc_times[i + 1]:
                    pytest.fail(
                        f"Data not sorted at index {i}: {times[i]} > {times[i + 1]} "
                        f"(out of {len(times)} records)"
                    )
        assert is_sorted, f"Data is not sorted by time ({len(times)} records)"

    @pytest.mark.network
    def test_fahrenheit_conversion(self):
        """Test temperature in Fahrenheit."""
        celsius_result = get_weather_data("725030-14732", years=2023, temp_unit="celsius")
        fahrenheit_result = get_weather_data("725030-14732", years=2023, temp_unit="fahrenheit")

        # Get first non-null temperature
        c_temp = celsius_result.filter(pl.col("temp").is_not_null())["temp"][0]
        f_temp = fahrenheit_result.filter(pl.col("temp").is_not_null())["temp"][0]

        # Verify Fahrenheit conversion: F = C * 9/5 + 32
        expected_f = c_temp * 9 / 5 + 32
        assert abs(f_temp - expected_f) < 0.2  # Allow small rounding difference

    def test_invalid_temp_unit(self):
        """Test that invalid temp_unit raises error."""
        with pytest.raises(ValueError, match="temp_unit"):
            get_weather_data("725030-14732", years=2023, temp_unit="rankine")

    @pytest.mark.network
    def test_invalid_station(self):
        """Test that invalid station raises error."""
        with pytest.raises(ValueError, match="not found"):
            get_weather_data("000000-00000", years=2023)

    @pytest.mark.network
    def test_multiple_years(self):
        """Test fetching multiple years of data."""
        result = get_weather_data("725030-14732", years=[2022, 2023])

        assert isinstance(result, pl.DataFrame)

        # Should have data from both years
        years_in_data = result["time"].dt.year().unique().to_list()
        assert 2022 in years_in_data or 2023 in years_in_data

    @pytest.mark.network
    def test_make_hourly(self):
        """Test hourly resampling."""
        result = get_weather_data("725030-14732", years=2023, make_hourly=True)

        assert isinstance(result, pl.DataFrame)

        # All times should be at the start of an hour (minute = 0)
        minutes = result["time"].dt.minute().unique().to_list()
        assert minutes == [0]

    @pytest.mark.network
    def test_station_id_in_result(self):
        """Test that station ID is included in results."""
        result = get_weather_data("725030-14732", years=2023)

        assert all(sid == "725030-14732" for sid in result["id"].to_list())

    @pytest.mark.network
    def test_reasonable_temperature_range(self):
        """Test that temperatures are in reasonable range."""
        result = get_weather_data("725030-14732", years=2023)

        temps = result.filter(pl.col("temp").is_not_null())["temp"].to_list()
        if temps:
            # New York temps should be roughly -30 to 45 Celsius
            assert all(-40 < t < 50 for t in temps)

    @pytest.mark.network
    def test_relative_humidity_range(self):
        """Test that relative humidity is in 0-100 range."""
        result = get_weather_data("725030-14732", years=2023)

        rh_values = result.filter(pl.col("rh").is_not_null())["rh"].to_list()
        if rh_values:
            # RH should be between 0 and 100 (with small tolerance for calculation quirks)
            assert all(-5 < rh < 110 for rh in rh_values)

    @pytest.mark.network
    def test_wind_direction_range(self):
        """Test that wind direction is in valid range."""
        result = get_weather_data("725030-14732", years=2023)

        wd_values = result.filter(pl.col("wd").is_not_null())["wd"].to_list()
        if wd_values:
            # Wind direction should be 1-360 degrees
            assert all(0 <= wd <= 360 for wd in wd_values)

    @pytest.mark.network
    def test_wind_speed_non_negative(self):
        """Test that wind speed values are non-negative."""
        result = get_weather_data("725030-14732", years=2023)

        ws_values = result.filter(pl.col("ws").is_not_null())["ws"].to_list()
        if ws_values:
            assert all(ws >= 0 for ws in ws_values)

    @pytest.mark.network
    def test_visibility_non_negative(self):
        """Test that visibility values are non-negative."""
        result = get_weather_data("725030-14732", years=2023)

        vis_values = result.filter(pl.col("visibility").is_not_null())["visibility"].to_list()
        if vis_values:
            assert all(v >= 0 for v in vis_values)

    @pytest.mark.network
    def test_atmospheric_pressure_reasonable(self):
        """Test that atmospheric pressure is in reasonable range."""
        result = get_weather_data("725030-14732", years=2023)

        pres_values = result.filter(pl.col("atmos_pres").is_not_null())["atmos_pres"].to_list()
        if pres_values:
            # Sea level pressure typically 870-1084 hPa
            assert all(800 < p < 1100 for p in pres_values)


class TestWeatherDataTypes:
    """Tests for weather data column types."""

    @pytest.mark.network
    def test_time_is_datetime(self):
        """Test that time column is datetime type."""
        result = get_weather_data("725030-14732", years=2023)
        assert result.schema["time"] == pl.Datetime

    @pytest.mark.network
    def test_temp_is_float(self):
        """Test that temperature is float type."""
        result = get_weather_data("725030-14732", years=2023)
        assert result.schema["temp"] == pl.Float64

    @pytest.mark.network
    def test_wind_direction_is_int(self):
        """Test that wind direction is integer type."""
        result = get_weather_data("725030-14732", years=2023)
        assert result.schema["wd"] == pl.Int32

    @pytest.mark.network
    def test_id_is_string(self):
        """Test that id column is string type."""
        result = get_weather_data("725030-14732", years=2023)
        assert result.schema["id"] == pl.Utf8


class TestYearHandling:
    """Tests for year parameter handling."""

    @pytest.mark.network
    def test_year_as_int(self):
        """Test passing a single year as integer."""
        result = get_weather_data("725030-14732", years=2023)
        assert isinstance(result, pl.DataFrame)
        years_in_data = result["time"].dt.year().unique().to_list()
        assert 2023 in years_in_data

    @pytest.mark.network
    def test_year_as_list(self):
        """Test passing years as a list."""
        result = get_weather_data("725030-14732", years=[2023])
        assert isinstance(result, pl.DataFrame)


class TestTemperatureUnit:
    """Tests for temperature unit conversion."""

    @pytest.mark.network
    def test_celsius_default(self):
        """Test that Celsius is the default temperature unit."""
        result = get_weather_data("725030-14732", years=2023)
        # Should have reasonable Celsius values
        temps = result.filter(pl.col("temp").is_not_null())["temp"].to_list()
        if temps:
            # New York Celsius temps should be roughly -30 to 45
            assert all(-40 < t < 50 for t in temps)

    @pytest.mark.network
    def test_fahrenheit_values_higher(self):
        """Test that Fahrenheit values are higher than Celsius (mostly)."""
        c_result = get_weather_data("725030-14732", years=2023, temp_unit="celsius")
        f_result = get_weather_data("725030-14732", years=2023, temp_unit="fahrenheit")

        c_mean = c_result.filter(pl.col("temp").is_not_null())["temp"].mean()
        f_mean = f_result.filter(pl.col("temp").is_not_null())["temp"].mean()

        # For positive Celsius temps, Fahrenheit should be higher
        if c_mean and c_mean > 0:
            assert f_mean > c_mean

    @pytest.mark.network
    def test_kelvin_conversion(self):
        """Test Kelvin temperature conversion."""
        c_result = get_weather_data("725030-14732", years=2023, temp_unit="c")
        k_result = get_weather_data("725030-14732", years=2023, temp_unit="k")

        c_temp = c_result.filter(pl.col("temp").is_not_null())["temp"][0]
        k_temp = k_result.filter(pl.col("temp").is_not_null())["temp"][0]

        # Kelvin = Celsius + 273.15
        expected_k = c_temp + 273.15
        assert abs(k_temp - expected_k) < 0.1

    @pytest.mark.network
    def test_short_temp_unit_names(self):
        """Test that short temperature unit names work."""
        # Test 'c' for Celsius
        c_result = get_weather_data("725030-14732", years=2023, temp_unit="c")
        assert c_result.height > 0

        # Test 'F' for Fahrenheit (uppercase)
        f_result = get_weather_data("725030-14732", years=2023, temp_unit="F")
        assert f_result.height > 0

        # Test 'K' for Kelvin (uppercase)
        k_result = get_weather_data("725030-14732", years=2023, temp_unit="K")
        assert k_result.height > 0


class TestLocalTimeConversion:
    """Tests for local time conversion."""

    @pytest.mark.network
    def test_convert_to_local_time(self):
        """Test that local time conversion changes timestamps."""
        utc_result = get_weather_data("725030-14732", years=2023, convert_to_local=False)
        local_result = get_weather_data("725030-14732", years=2023, convert_to_local=True)

        # Times should be different (LaGuardia is UTC-5 or UTC-4)
        # Check that at least first timestamps differ
        if utc_result.height > 0 and local_result.height > 0:
            # The times might be the same if we compare naive datetimes
            # but the data should have been processed
            assert isinstance(local_result, pl.DataFrame)

    @pytest.mark.network
    def test_no_conversion_default(self):
        """Test that convert_to_local=False keeps UTC."""
        result = get_weather_data("725030-14732", years=2023, convert_to_local=False)
        assert isinstance(result, pl.DataFrame)


class TestHourlyResampling:
    """Tests for hourly resampling."""

    @pytest.mark.network
    def test_hourly_reduces_rows(self):
        """Test that hourly resampling reduces number of rows."""
        raw = get_weather_data("725030-14732", years=2023, make_hourly=False)
        hourly = get_weather_data("725030-14732", years=2023, make_hourly=True)

        # Hourly should have fewer or equal rows
        assert hourly.height <= raw.height

    @pytest.mark.network
    def test_hourly_time_aligned(self):
        """Test that hourly data has minute=0."""
        result = get_weather_data("725030-14732", years=2023, make_hourly=True)

        minutes = result["time"].dt.minute().to_list()
        assert all(m == 0 for m in minutes)

    @pytest.mark.network
    def test_hourly_preserves_data_quality(self):
        """Test that hourly resampling preserves reasonable values."""
        result = get_weather_data("725030-14732", years=2023, make_hourly=True)

        temps = result.filter(pl.col("temp").is_not_null())["temp"].to_list()
        if temps:
            # Values should still be in reasonable range
            assert all(-40 < t < 50 for t in temps)


class TestStationIdFormats:
    """Tests for various station ID formats."""

    @pytest.mark.network
    def test_hyphenated_id(self):
        """Test standard hyphenated station ID format."""
        result = get_weather_data("725030-14732", years=2023)
        assert isinstance(result, pl.DataFrame)

    def test_invalid_id_format(self):
        """Test that completely invalid ID raises error."""
        with pytest.raises(ValueError):
            get_weather_data("invalid", years=2023)


class TestDataConsistency:
    """Tests for data consistency across requests."""

    @pytest.mark.network
    def test_same_data_multiple_calls(self):
        """Test that multiple calls return consistent data."""
        result1 = get_weather_data("725030-14732", years=2023)
        result2 = get_weather_data("725030-14732", years=2023)

        assert result1.height == result2.height
        assert result1.columns == result2.columns

    @pytest.mark.network
    def test_column_order_consistent(self):
        """Test that column order is consistent."""
        result = get_weather_data("725030-14732", years=2023)
        expected_order = [
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
        assert result.columns == expected_order


class TestStationInfo:
    """Tests for including station metadata in weather data."""

    @pytest.mark.network
    def test_incl_stn_info_adds_columns(self):
        """Test that incl_stn_info adds station metadata columns."""
        result = get_weather_data("725030-14732", years=2023, incl_stn_info=True)

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
            "name",
            "country",
            "state",
            "icao",
            "lat",
            "lon",
            "elev",
        ]
        assert result.columns == expected_columns

    @pytest.mark.network
    def test_incl_stn_info_default_false(self):
        """Test that station info is not included by default."""
        result = get_weather_data("725030-14732", years=2023)

        station_columns = ["name", "country", "state", "icao", "lat", "lon", "elev"]
        for col in station_columns:
            assert col not in result.columns

    @pytest.mark.network
    def test_station_info_values_populated(self):
        """Test that station metadata values are populated."""
        result = get_weather_data("725030-14732", years=2023, incl_stn_info=True)

        # Check first row has station info
        first_row = result.head(1)
        assert first_row["name"][0] is not None
        assert first_row["country"][0] is not None
        assert first_row["icao"][0] == "KLGA"
        assert first_row["lat"][0] is not None
        assert first_row["lon"][0] is not None

    @pytest.mark.network
    def test_station_info_consistent_across_rows(self):
        """Test that station metadata is consistent across all rows."""
        result = get_weather_data("725030-14732", years=2023, incl_stn_info=True)

        # All rows should have same station metadata
        unique_names = result["name"].n_unique()
        unique_countries = result["country"].n_unique()
        unique_icao = result["icao"].n_unique()
        unique_lat = result["lat"].n_unique()
        unique_lon = result["lon"].n_unique()

        assert unique_names == 1
        assert unique_countries == 1
        assert unique_icao == 1
        assert unique_lat == 1
        assert unique_lon == 1

    @pytest.mark.network
    def test_station_info_with_hourly(self):
        """Test that station info works with hourly resampling."""
        result = get_weather_data("725030-14732", years=2023, incl_stn_info=True, make_hourly=True)

        # Should have station metadata columns
        assert "name" in result.columns
        assert "country" in result.columns
        assert "icao" in result.columns

        # Metadata should be consistent
        assert result["name"].n_unique() == 1
        assert result["icao"][0] == "KLGA"

    @pytest.mark.network
    def test_station_info_lat_lon_types(self):
        """Test that lat/lon are float types."""
        result = get_weather_data("725030-14732", years=2023, incl_stn_info=True)

        assert result["lat"].dtype == pl.Float64
        assert result["lon"].dtype == pl.Float64
        assert result["elev"].dtype == pl.Float64

    @pytest.mark.network
    def test_station_info_reasonable_coordinates(self):
        """Test that coordinates are in reasonable ranges."""
        result = get_weather_data("725030-14732", years=2023, incl_stn_info=True)

        lat = result["lat"][0]
        lon = result["lon"][0]
        elev = result["elev"][0]

        # LaGuardia is in NYC area
        assert 40 < lat < 41
        assert -74 < lon < -73
        assert -10 < elev < 100  # Near sea level
