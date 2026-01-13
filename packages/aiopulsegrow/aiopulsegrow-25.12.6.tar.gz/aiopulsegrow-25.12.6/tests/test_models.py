"""Tests for data models."""

from aiopulsegrow.models import (
    Device,
    DeviceData,
)
from tests.fixtures.mock_data import ALL_DEVICES


class TestDevice:
    """Test Device model."""

    def test_from_dict(self):
        """Test creating Device from dict using real API data."""
        data = ALL_DEVICES["deviceViewDtos"][0]
        device = Device.from_dict(data)
        assert device.id == 20447
        assert device.name == "PulsePro"
        assert device.device_type == 1


class TestDeviceData:
    """Test DeviceData model."""

    def test_from_dict(self):
        """Test creating DeviceData from dict with real API format."""
        device_data = DeviceData.from_dict(ALL_DEVICES)
        assert len(device_data.devices) == 1
        assert len(device_data.sensors) == 2
        assert device_data.devices[0].id == 20447
        assert device_data.sensors[0].id == 1638
