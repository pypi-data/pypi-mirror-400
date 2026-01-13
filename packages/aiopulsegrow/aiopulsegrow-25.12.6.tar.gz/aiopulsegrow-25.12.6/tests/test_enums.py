"""Tests for Pulsegrow enums."""

from aiopulsegrow.enums import (
    DeviceType,
    HubThresholdType,
    ParSensorSubtype,
    SensorThresholdType,
    SensorType,
    ThresholdType,
    TimelineEventType,
    UserGrowRole,
)


class TestDeviceType:
    """Test DeviceType enum."""

    def test_pulse_one(self):
        """Test PulseOne device type."""
        assert DeviceType.PULSE_ONE == 0
        assert DeviceType.PULSE_ONE.name == "PULSE_ONE"

    def test_pulse_pro(self):
        """Test PulsePro device type."""
        assert DeviceType.PULSE_PRO == 1
        assert DeviceType.PULSE_PRO.name == "PULSE_PRO"

    def test_pulse_hub(self):
        """Test PulseHub device type."""
        assert DeviceType.PULSE_HUB == 2
        assert DeviceType.PULSE_HUB.name == "PULSE_HUB"

    def test_sensor(self):
        """Test Sensor device type."""
        assert DeviceType.SENSOR == 3
        assert DeviceType.SENSOR.name == "SENSOR"

    def test_control(self):
        """Test Control device type."""
        assert DeviceType.CONTROL == 4
        assert DeviceType.CONTROL.name == "CONTROL"

    def test_pulse_zero(self):
        """Test PulseZero device type."""
        assert DeviceType.PULSE_ZERO == 5
        assert DeviceType.PULSE_ZERO.name == "PULSE_ZERO"

    def test_can_compare_with_int(self):
        """Test that enum values can be compared with integers."""
        device_type = 1
        assert device_type == DeviceType.PULSE_PRO
        assert DeviceType(device_type) == DeviceType.PULSE_PRO


class TestSensorType:
    """Test SensorType enum."""

    def test_hub(self):
        """Test Hub sensor type."""
        assert SensorType.HUB == 0

    def test_ph10(self):
        """Test pH 1.0 sensor type."""
        assert SensorType.PH10 == 3
        assert SensorType.PH10.name == "PH10"

    def test_ec1(self):
        """Test EC1 sensor type."""
        assert SensorType.EC1 == 4
        assert SensorType.EC1.name == "EC1"

    def test_par1(self):
        """Test PAR1 sensor type."""
        assert SensorType.PAR1 == 8

    def test_can_compare_with_int(self):
        """Test that enum values can be compared with integers."""
        sensor_type = 3
        assert sensor_type == SensorType.PH10
        assert SensorType(sensor_type) == SensorType.PH10


class TestTimelineEventType:
    """Test TimelineEventType enum."""

    def test_note(self):
        """Test note event type."""
        assert TimelineEventType.NOTE == 1

    def test_notification(self):
        """Test notification event type."""
        assert TimelineEventType.NOTIFICATION == 2
        assert TimelineEventType.NOTIFICATION.name == "NOTIFICATION"

    def test_sensor_calibrated(self):
        """Test sensor calibration event type."""
        assert TimelineEventType.SENSOR_CALIBRATED == 8
        assert TimelineEventType.SENSOR_CALIBRATED.name == "SENSOR_CALIBRATED"

    def test_can_compare_with_int(self):
        """Test that enum values can be compared with integers."""
        event_type = 2
        assert event_type == TimelineEventType.NOTIFICATION
        assert TimelineEventType(event_type) == TimelineEventType.NOTIFICATION


class TestThresholdType:
    """Test ThresholdType enum (device thresholds)."""

    def test_light(self):
        """Test light threshold type."""
        assert ThresholdType.LIGHT == 1

    def test_temperature(self):
        """Test temperature threshold type."""
        assert ThresholdType.TEMPERATURE == 2

    def test_battery_v(self):
        """Test battery voltage threshold type."""
        assert ThresholdType.BATTERY_V == 6

    def test_vpd(self):
        """Test VPD threshold type."""
        assert ThresholdType.VPD == 11

    def test_can_compare_with_int(self):
        """Test that enum values can be compared with integers."""
        threshold_type = 2
        assert threshold_type == ThresholdType.TEMPERATURE
        assert ThresholdType(threshold_type) == ThresholdType.TEMPERATURE


class TestSensorThresholdType:
    """Test SensorThresholdType enum."""

    def test_ph(self):
        """Test pH threshold type."""
        assert SensorThresholdType.PH == 6
        assert SensorThresholdType.PH.name == "PH"

    def test_ec1_ec(self):
        """Test EC1 EC threshold type."""
        assert SensorThresholdType.EC1_EC == 7

    def test_par1_ppfd(self):
        """Test PAR1 PPFD threshold type."""
        assert SensorThresholdType.PAR1_PPFD == 12

    def test_can_compare_with_int(self):
        """Test that enum values can be compared with integers."""
        threshold_type = 6
        assert threshold_type == SensorThresholdType.PH
        assert SensorThresholdType(threshold_type) == SensorThresholdType.PH


class TestHubThresholdType:
    """Test HubThresholdType enum."""

    def test_power(self):
        """Test hub power threshold type."""
        assert HubThresholdType.POWER == 1
        assert HubThresholdType.POWER.name == "POWER"

    def test_connectivity(self):
        """Test hub connectivity threshold type."""
        assert HubThresholdType.CONNECTIVITY == 2
        assert HubThresholdType.CONNECTIVITY.name == "CONNECTIVITY"

    def test_can_compare_with_int(self):
        """Test that enum values can be compared with integers."""
        threshold_type = 1
        assert threshold_type == HubThresholdType.POWER
        assert HubThresholdType(threshold_type) == HubThresholdType.POWER


class TestParSensorSubtype:
    """Test ParSensorSubtype enum."""

    def test_sq522(self):
        """Test SQ-522 sensor subtype."""
        assert ParSensorSubtype.SQ522 == 0
        assert ParSensorSubtype.SQ522.name == "SQ522"

    def test_sq618(self):
        """Test SQ-618 sensor subtype."""
        assert ParSensorSubtype.SQ618 == 1
        assert ParSensorSubtype.SQ618.name == "SQ618"

    def test_can_compare_with_int(self):
        """Test that enum values can be compared with integers."""
        subtype = 0
        assert subtype == ParSensorSubtype.SQ522
        assert ParSensorSubtype(subtype) == ParSensorSubtype.SQ522


class TestUserGrowRole:
    """Test UserGrowRole enum."""

    def test_owner(self):
        """Test owner role."""
        assert UserGrowRole.OWNER == 0
        assert UserGrowRole.OWNER.name == "OWNER"

    def test_admin(self):
        """Test admin role."""
        assert UserGrowRole.ADMIN == 1

    def test_editor(self):
        """Test editor role."""
        assert UserGrowRole.EDITOR == 2

    def test_viewer(self):
        """Test viewer role."""
        assert UserGrowRole.VIEWER == 3

    def test_can_compare_with_int(self):
        """Test that enum values can be compared with integers."""
        role = 0
        assert role == UserGrowRole.OWNER
        assert UserGrowRole(role) == UserGrowRole.OWNER
