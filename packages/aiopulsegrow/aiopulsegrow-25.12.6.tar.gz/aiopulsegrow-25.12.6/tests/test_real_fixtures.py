"""Tests using real API mock data from fixtures.

NOTE: If you get import errors about 'null' not being defined, you need to
regenerate the mock_data.py file with the updated script:
    python scripts/fetch_mock_data.py YOUR_API_KEY
"""

import pytest

from aiopulsegrow.enums import (
    DeviceType,
    SensorThresholdType,
    SensorType,
    TimelineEventType,
)
from aiopulsegrow.models import (
    Device,
    DeviceData,
    DeviceDataPoint,
    Hub,
    LightReading,
    Sensor,
    SensorDetails,
    TimelineEvent,
    TriggeredThreshold,
    UserUsage,
)

try:
    from tests.fixtures.mock_data import (
        ALL_DEVICES,
        DATA_RANGE,
        HUB_DETAILS,
        HUB_IDS,
        LIGHT_READINGS,
        RECENT_DATA,
        SENSOR_DATA,
        SENSOR_DETAILS,
        TIMELINE,
        TRIGGERED_THRESHOLDS,
        USER_USAGE,
    )
except (ImportError, NameError):
    pytest.skip(
        "Mock data fixtures not available or need regeneration. "
        "Run: python scripts/fetch_mock_data.py YOUR_API_KEY",
        allow_module_level=True,
    )


class TestRealFixtures:
    """Test models with real API response data."""

    def test_all_devices_parsing(self):
        """Test parsing real /all-devices response."""
        device_data = DeviceData.from_dict(ALL_DEVICES)

        # Should have parsed devices
        assert isinstance(device_data, DeviceData)
        assert len(device_data.devices) > 0
        assert len(device_data.sensors) > 0

        # Check first device (types are now int per OpenAPI spec)
        first_device = device_data.devices[0]
        assert isinstance(first_device, Device)
        assert first_device.id == 20447
        assert first_device.name == "PulsePro"
        assert first_device.device_type == 1

        # Check first sensor (types are now int per OpenAPI spec)
        first_sensor = device_data.sensors[0]
        assert isinstance(first_sensor, Sensor)
        assert first_sensor.id == 1638
        assert first_sensor.sensor_type == 3
        assert first_sensor.hub_id == 402

    def test_hub_ids_parsing(self):
        """Test parsing real /hubs/ids response."""
        assert isinstance(HUB_IDS, list)
        assert len(HUB_IDS) > 0
        assert all(isinstance(hub_id, int) for hub_id in HUB_IDS)

    def test_hub_details_parsing(self):
        """Test parsing real /hubs/{id} response."""
        hub = Hub.from_dict(HUB_DETAILS)

        assert isinstance(hub, Hub)
        assert hub.id == 402
        assert hub.name is not None
        assert hub.grow_id == 17513
        assert hub.mac_address == "0c2a6914e40e"
        assert hub.hidden is False
        assert hub.hub_thresholds is not None
        assert isinstance(hub.hub_thresholds, list)
        assert hub.sensor_devices is not None
        assert isinstance(hub.sensor_devices, list)

    def test_device_with_real_data(self):
        """Test that Device model handles real API deviceViewDto structure."""
        device_dto = ALL_DEVICES["deviceViewDtos"][0]
        device = Device.from_dict(device_dto)

        assert device.id == 20447
        assert device.name == "PulsePro"
        assert device.device_type == 1  # int per OpenAPI spec

        # Test nested mostRecentDataPoint
        assert device.most_recent_data_point is not None
        assert device.most_recent_data_point.device_id == 20447
        assert device.most_recent_data_point.temperature_f is not None
        assert device.most_recent_data_point.co2 is not None

        # Test nested proLightReadingPreviewDto
        assert device.pro_light_reading_preview is not None
        assert device.pro_light_reading_preview.id is not None
        assert device.pro_light_reading_preview.ppfd is not None
        assert device.pro_light_reading_preview.dli is not None

        # Test other device fields
        assert device.grow_id == 17513
        assert device.day_start == "08:00:00"
        assert device.night_start == "20:00:00"
        assert device.is_day is not None
        assert device.battery_count == 1
        assert device.low_battery_voltage == 3.7

    def test_sensor_with_real_data(self):
        """Test that Sensor model handles real API universalSensorViews structure."""
        sensor_view = ALL_DEVICES["universalSensorViews"][0]
        sensor = Sensor.from_dict(sensor_view)

        assert sensor.id == 1638
        assert sensor.sensor_type == 3  # int per OpenAPI spec

        # Test all sensor fields
        assert sensor.hub_id == 402
        assert sensor.grow_id == 17513
        assert sensor.device_type == 3  # int per OpenAPI spec
        assert sensor.day_start == "08:00:00"
        assert sensor.night_start == "20:00:00"
        assert sensor.display_order == 2
        assert sensor.hidden is False
        assert sensor.par_sensor_subtype is None
        assert sensor.template_id is None

        # Test nested data
        assert sensor.most_recent_data_point is not None
        assert sensor.most_recent_data_point.sensor_id == 1638
        assert len(sensor.most_recent_data_point.data_point_values) == 1
        assert sensor.most_recent_data_point.data_point_values[0].param_name == "pH"
        assert sensor.most_recent_data_point.data_point_values[0].param_value is not None
        assert float(sensor.most_recent_data_point.data_point_values[0].param_value) > 0

        assert sensor.last_hour_data_point_dtos is not None
        assert isinstance(sensor.last_hour_data_point_dtos, dict)

    def test_timeline_events_parsing(self):
        """Test parsing real /api/timeline response."""
        assert isinstance(TIMELINE, list)
        assert len(TIMELINE) > 0

        # Test first timeline event
        first_event = TimelineEvent.from_dict(TIMELINE[0])
        assert isinstance(first_event, TimelineEvent)
        assert first_event.id == 42834836
        assert first_event.timeline_event_type == 2
        assert first_event.title == "Your Nighttime Ph is High  in PH Sensor ID: 1638."
        assert first_event.detail == "Reading: 6.5, Limit: 6.4"
        assert first_event.display is True
        assert first_event.grow_id == 17513
        assert first_event.created_at is not None
        assert first_event.updated_at is not None

    def test_triggered_thresholds_parsing(self):
        """Test parsing real /api/triggered-thresholds response."""
        assert isinstance(TRIGGERED_THRESHOLDS, dict)
        assert "ongoing" in TRIGGERED_THRESHOLDS
        assert "resolved" in TRIGGERED_THRESHOLDS
        assert "growId" in TRIGGERED_THRESHOLDS

        # Test resolved thresholds
        resolved = TRIGGERED_THRESHOLDS["resolved"]
        assert isinstance(resolved, list)
        assert len(resolved) > 0

        # Test first resolved threshold
        first_threshold = TriggeredThreshold.from_dict(resolved[0])
        assert isinstance(first_threshold, TriggeredThreshold)
        assert first_threshold.id == 1229890
        assert first_threshold.device_id == 1638
        assert first_threshold.device_name == "PH Sensor ID: 1638"
        assert first_threshold.low_or_high is True
        assert first_threshold.low_threshold_value == 5.2
        assert first_threshold.high_threshold_value == 6.4
        assert first_threshold.triggering_value == "6.5"
        assert first_threshold.sensor_threshold_type == 6
        assert first_threshold.hub_threshold_type is None
        assert first_threshold.threshold_id is None
        # Note: thresholdType can be None for sensor thresholds
        assert first_threshold.resolved is False
        assert first_threshold.created_at is not None
        assert first_threshold.resolved_at is not None

    def test_user_usage_parsing(self):
        """Test parsing real /users response."""
        assert isinstance(USER_USAGE, list)
        assert len(USER_USAGE) > 0

        # Test first user
        first_user = UserUsage.from_dict(USER_USAGE[0])
        assert isinstance(first_user, UserUsage)
        assert first_user.user_id == 17425
        assert first_user.user_email == "pascal@vizeli.ch"
        assert first_user.user_name == "pascal@vizeli.ch"
        assert first_user.role == "Owner"
        assert first_user.last_active is not None

    def test_hub_view_from_all_devices(self):
        """Test parsing hubViewDtos from /all-devices response."""
        hub_views = ALL_DEVICES.get("hubViewDtos", [])
        assert len(hub_views) > 0

        first_hub = hub_views[0]
        assert first_hub["id"] == 402
        assert first_hub["name"] == "PulseHub"
        assert first_hub["deviceType"] == 2
        assert first_hub["displayOrder"] == 1
        assert first_hub["growId"] == 17513
        assert first_hub["hidden"] is False

        # Test nested mostRecentDataPoint
        assert "mostRecentDataPoint" in first_hub
        most_recent = first_hub["mostRecentDataPoint"]
        assert most_recent["deviceId"] == 402
        assert "signalStrength" in most_recent
        assert most_recent["signalStrength"] is not None

    def test_ec_sensor_with_multiple_values(self):
        """Test EC sensor with multiple parameter values."""
        ec_sensor_view = ALL_DEVICES["universalSensorViews"][1]
        ec_sensor = Sensor.from_dict(ec_sensor_view)

        assert ec_sensor.id == 1696
        assert ec_sensor.sensor_type == 4  # int per OpenAPI spec
        assert ec_sensor.name == "EC1 Sensor ID: 1696"

        # Test EC sensor has multiple parameter values
        assert ec_sensor.most_recent_data_point is not None
        assert len(ec_sensor.most_recent_data_point.data_point_values) == 2

        # Check EC value
        ec_value = ec_sensor.most_recent_data_point.data_point_values[0]
        assert ec_value.param_name == "EC"
        assert ec_value.param_value is not None
        assert ec_value.measuring_unit == "mS/cm"

        # Check Temperature value
        temp_value = ec_sensor.most_recent_data_point.data_point_values[1]
        assert temp_value.param_name == "Temperature"
        assert temp_value.param_value is not None
        assert temp_value.measuring_unit == "°C"

    def test_enums_match_real_data(self):
        """Test that enum values match actual API data."""
        # Test device types
        pulse_pro = ALL_DEVICES["deviceViewDtos"][0]
        assert pulse_pro["deviceType"] == DeviceType.PULSE_PRO

        pulse_hub = ALL_DEVICES["hubViewDtos"][0]
        assert pulse_hub["deviceType"] == DeviceType.PULSE_HUB

        # Test sensor types
        ph_sensor_view = ALL_DEVICES["universalSensorViews"][0]
        assert ph_sensor_view["sensorType"] == SensorType.PH10
        assert ph_sensor_view["deviceType"] == DeviceType.SENSOR

        ec_sensor_view = ALL_DEVICES["universalSensorViews"][1]
        assert ec_sensor_view["sensorType"] == SensorType.EC1

        # Test timeline event types
        for event in TIMELINE:
            event_type = event.get("timelineEventType")
            if event_type == 2:
                assert event_type == TimelineEventType.NOTIFICATION
            elif event_type == 8:
                assert event_type == TimelineEventType.SENSOR_CALIBRATED

        # Test sensor threshold types
        for threshold in TRIGGERED_THRESHOLDS["resolved"]:
            threshold_type = threshold.get("sensorThresholdType")
            if threshold_type == 6:
                assert threshold_type == SensorThresholdType.PH

    def test_device_recent_data_parsing(self):
        """Test parsing real device recent data response."""
        device_data = DeviceDataPoint.from_dict(RECENT_DATA)

        assert isinstance(device_data, DeviceDataPoint)
        assert device_data.device_type == 1  # int per OpenAPI spec
        assert device_data.temperature_f is not None
        assert device_data.temperature_c is not None
        assert device_data.humidity_rh is not None
        assert device_data.vpd is not None
        assert device_data.dp_f is not None
        assert device_data.dp_c is not None
        assert device_data.light_lux is not None
        assert device_data.air_pressure is not None

        # Test light calculation reading
        assert device_data.light_calculation_reading is not None
        assert "ppfd" in device_data.light_calculation_reading
        assert "channels" in device_data.light_calculation_reading

    def test_device_data_range_parsing(self):
        """Test parsing real device data range response."""
        assert isinstance(DATA_RANGE, list)
        assert len(DATA_RANGE) > 0

        # Test first data point
        first_point = DeviceDataPoint.from_dict(DATA_RANGE[0])
        assert isinstance(first_point, DeviceDataPoint)
        assert first_point.device_type == 1  # int per OpenAPI spec
        assert first_point.temperature_f is not None
        assert first_point.humidity_rh is not None
        assert first_point.vpd is not None

    def test_light_readings_parsing(self):
        """Test parsing real light readings response."""
        assert isinstance(LIGHT_READINGS, dict)
        assert "currentPage" in LIGHT_READINGS
        assert "numPages" in LIGHT_READINGS
        assert "lightReadings" in LIGHT_READINGS
        assert LIGHT_READINGS["currentPage"] == 1
        assert LIGHT_READINGS["numPages"] > 0

        assert len(LIGHT_READINGS["lightReadings"]) > 0
        first_reading_data = LIGHT_READINGS["lightReadings"][0]

        # Test the raw data structure
        assert first_reading_data["deviceId"] == 20447
        assert first_reading_data["id"] is not None
        assert first_reading_data["createdAt"] is not None
        assert first_reading_data["ppfd"] is not None
        assert first_reading_data["dli"] is not None

        # Test spectrum channels
        assert first_reading_data["channel1"] is not None
        assert first_reading_data["channel2"] is not None
        assert first_reading_data["channel3"] is not None
        assert first_reading_data["channel4"] is not None
        assert first_reading_data["channel5"] is not None
        assert first_reading_data["channel6"] is not None
        assert first_reading_data["channel7"] is not None
        assert first_reading_data["channel8"] is not None

        # Test other light parameters
        assert first_reading_data["clear"] is not None
        assert first_reading_data["gain"] is not None
        assert first_reading_data["tint"] is not None
        assert first_reading_data["pfdRed"] is not None
        assert first_reading_data["pfdGreen"] is not None
        assert first_reading_data["pfdBlue"] is not None

        # Test that LightReading model can parse the data
        first_reading = LightReading.from_dict(first_reading_data)
        assert isinstance(first_reading, LightReading)
        assert first_reading.ppfd is not None
        assert first_reading.dli is not None

    def test_sensor_details_parsing(self):
        """Test parsing real sensor details response."""
        assert isinstance(SENSOR_DETAILS, dict)
        assert SENSOR_DETAILS["id"] == 1638
        assert SENSOR_DETAILS["name"] == "PH Sensor ID: 1638"
        assert SENSOR_DETAILS["sensorType"] == 3
        assert SENSOR_DETAILS["growId"] == 17513
        assert SENSOR_DETAILS["hubId"] == 402
        assert SENSOR_DETAILS["hubName"] == "PulseHub"
        assert SENSOR_DETAILS["hidden"] is False
        assert SENSOR_DETAILS["dayStart"] == "08:00:00"
        assert SENSOR_DETAILS["nightStart"] == "20:00:00"

        assert "thresholds" in SENSOR_DETAILS
        assert isinstance(SENSOR_DETAILS["thresholds"], list)
        if len(SENSOR_DETAILS["thresholds"]) > 0:
            first_threshold = SENSOR_DETAILS["thresholds"][0]
            assert "thresholdType" in first_threshold

        sensor_details = SensorDetails.from_dict(SENSOR_DETAILS)
        assert isinstance(sensor_details, SensorDetails)
        assert sensor_details.id == 1638
        assert sensor_details.name == "PH Sensor ID: 1638"

    def test_sensor_data_range_parsing(self):
        """Test parsing real sensor data range response (can be empty)."""
        assert isinstance(SENSOR_DATA, dict)
        assert "dataPointValues" in SENSOR_DATA
        assert "dataPointValuesCreatedAt" in SENSOR_DATA

        if SENSOR_DATA.get("dataPointValues"):
            assert isinstance(SENSOR_DATA["dataPointValues"], list)
        if SENSOR_DATA.get("dataPointValuesCreatedAt"):
            assert isinstance(SENSOR_DATA["dataPointValuesCreatedAt"], list)

    def test_all_mock_data_available(self):
        """Test that all expected mock data constants are available."""
        assert ALL_DEVICES is not None
        assert HUB_IDS is not None
        assert HUB_DETAILS is not None
        assert TIMELINE is not None
        assert TRIGGERED_THRESHOLDS is not None
        assert USER_USAGE is not None
        assert RECENT_DATA is not None
        assert DATA_RANGE is not None
        assert LIGHT_READINGS is not None
        assert SENSOR_DETAILS is not None
        assert SENSOR_DATA is not None

        assert isinstance(ALL_DEVICES, dict)
        assert isinstance(HUB_IDS, list)
        assert isinstance(HUB_DETAILS, dict)
        assert isinstance(TIMELINE, list)
        assert isinstance(TRIGGERED_THRESHOLDS, dict)
        assert isinstance(USER_USAGE, list)
        assert isinstance(RECENT_DATA, dict)
        assert isinstance(DATA_RANGE, list)
        assert isinstance(LIGHT_READINGS, dict)
        assert isinstance(SENSOR_DETAILS, dict)
        assert isinstance(SENSOR_DATA, dict)
