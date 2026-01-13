"""Data models for Pulsegrow API responses.

Field requirements are based on the official Pulsegrow OpenAPI specification.
Required fields will raise KeyError if missing from API response.
Optional fields default to None or appropriate zero values.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ProLightReadingPreview:
    """Preview of professional light reading data (ProLightReadingPreviewDto)."""

    id: int
    ppfd: float
    dli: float
    created_at: datetime

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProLightReadingPreview:
        """Create a ProLightReadingPreview from API response data."""
        created_at = _parse_datetime(data.get("createdAt"))
        if created_at is None:
            raise ValueError("createdAt is required for ProLightReadingPreview")
        return cls(
            id=data["id"],
            ppfd=data["ppfd"],
            dli=data["dli"],
            created_at=created_at,
        )


@dataclass
class Device:
    """Represents a Pulsegrow device (DeviceViewDto).

    Based on OpenAPI spec, required fields are:
    id, growId, hidden, deviceType, guid, pulseGuid, isDay, vpdLeafTempOffsetInF,
    batteryCount, lowBatteryVoltage, mostRecentDataPoint, growTimezoneOffset
    """

    # Required fields per OpenAPI spec
    id: int
    grow_id: int
    hidden: bool
    device_type: int
    guid: str
    pulse_guid: str
    is_day: bool
    vpd_leaf_temp_offset_in_f: float
    battery_count: int
    low_battery_voltage: float
    grow_timezone_offset: int

    # Optional fields per OpenAPI spec
    display_order: int = 0
    name: str | None = None
    template_id: int | None = None
    vpd_target: float | None = None
    day_start: str | None = None
    night_start: str | None = None

    # Nested data
    most_recent_data_point: DeviceDataPoint | None = None
    pro_light_reading_preview: ProLightReadingPreview | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Device:
        """Create a Device from API response data (DeviceViewDto or DeviceDetailsDto)."""
        # Parse nested mostRecentDataPoint if present
        most_recent = None
        if "mostRecentDataPoint" in data and data["mostRecentDataPoint"]:
            most_recent = DeviceDataPoint.from_dict(data["mostRecentDataPoint"])

        # Parse nested proLightReadingPreviewDto if present
        light_preview = None
        if "proLightReadingPreviewDto" in data and data["proLightReadingPreviewDto"]:
            light_preview = ProLightReadingPreview.from_dict(data["proLightReadingPreviewDto"])

        return cls(
            id=data["id"],
            grow_id=data["growId"],
            hidden=data["hidden"],
            device_type=data["deviceType"],
            guid=data["guid"],
            pulse_guid=data["pulseGuid"],
            is_day=data["isDay"],
            vpd_leaf_temp_offset_in_f=data["vpdLeafTempOffsetInF"],
            battery_count=data["batteryCount"],
            low_battery_voltage=data["lowBatteryVoltage"],
            grow_timezone_offset=data["growTimezoneOffset"],
            display_order=data.get("displayOrder", 0),
            name=data.get("name"),
            template_id=data.get("templateId"),
            vpd_target=data.get("vpdTarget"),
            day_start=data.get("dayStart"),
            night_start=data.get("nightStart"),
            most_recent_data_point=most_recent,
            pro_light_reading_preview=light_preview,
        )


@dataclass
class Sensor:
    """Represents a sensor (SensorDeviceViewUniversalDto).

    Based on OpenAPI spec, required fields are:
    id, growId, hidden, deviceType, sensorType, mostRecentDataPoint
    """

    # Required fields per OpenAPI spec
    id: int
    grow_id: int
    hidden: bool
    device_type: int
    sensor_type: int

    # Optional fields per OpenAPI spec
    display_order: int = 0
    name: str | None = None
    hub_id: int | None = None
    template_id: int | None = None
    day_start: str | None = None
    night_start: str | None = None
    par_sensor_subtype: int | None = None

    # Nested data
    most_recent_data_point: SensorDataPoint | None = None
    last_hour_data_point_dtos: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Sensor:
        """Create a Sensor from universalSensorViews API response."""
        # Parse nested mostRecentDataPoint if present
        most_recent = None
        if "mostRecentDataPoint" in data and data["mostRecentDataPoint"]:
            most_recent = SensorDataPoint.from_dict(data["mostRecentDataPoint"])

        return cls(
            id=data["id"],
            grow_id=data["growId"],
            hidden=data["hidden"],
            device_type=data["deviceType"],
            sensor_type=data["sensorType"],
            display_order=data.get("displayOrder", 0),
            name=data.get("name"),
            hub_id=data.get("hubId"),
            template_id=data.get("templateId"),
            day_start=data.get("dayStart"),
            night_start=data.get("nightStart"),
            par_sensor_subtype=data.get("parSensorSubtype"),
            most_recent_data_point=most_recent,
            last_hour_data_point_dtos=data.get("lastHourDataPointDtos"),
        )


@dataclass
class DeviceDataPoint:
    """Represents a device data point (PublicApiDataPoint).

    Based on OpenAPI spec, required fields are:
    deviceId, pluggedIn, signalStrength, createdAt, deviceType
    """

    # Required fields per OpenAPI spec
    device_id: int
    plugged_in: bool
    signal_strength: int
    created_at: datetime
    device_type: int

    # Optional fields per OpenAPI spec (with sensible defaults)
    battery_v: float | None = None
    temperature_f: float | None = None
    humidity_rh: float | None = None
    light_lux: float | None = None
    air_pressure: float | None = None
    vpd: float | None = None
    dp_c: float | None = None
    dp_f: float | None = None
    temperature_c: float | None = None
    co2: int | None = None
    co2_temperature: float | None = None
    co2_rh: float | None = None
    voc: int | None = None
    channel1: float | None = None
    channel2: float | None = None
    channel3: float | None = None
    channel4: float | None = None
    channel5: float | None = None
    channel6: float | None = None
    channel7: float | None = None
    channel8: float | None = None
    near: float | None = None
    clear: float | None = None
    flicker: float | None = None
    par: float | None = None
    gain: int | None = None
    tint: float | None = None
    light_calculation_reading: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DeviceDataPoint:
        """Create a DeviceDataPoint from API response data."""
        created_at = _parse_datetime(data.get("createdAt"))
        if created_at is None:
            raise ValueError("createdAt is required for DeviceDataPoint")

        return cls(
            device_id=data["deviceId"],
            plugged_in=data["pluggedIn"],
            signal_strength=data["signalStrength"],
            created_at=created_at,
            device_type=data["deviceType"],
            battery_v=data.get("batteryV"),
            temperature_f=data.get("temperatureF"),
            humidity_rh=data.get("humidityRh"),
            light_lux=data.get("lightLux"),
            air_pressure=data.get("airPressure"),
            vpd=data.get("vpd"),
            dp_c=data.get("dpC"),
            dp_f=data.get("dpF"),
            temperature_c=data.get("temperatureC"),
            co2=data.get("co2"),
            co2_temperature=data.get("co2Temperature"),
            co2_rh=data.get("co2Rh"),
            voc=data.get("voc"),
            channel1=data.get("channel1"),
            channel2=data.get("channel2"),
            channel3=data.get("channel3"),
            channel4=data.get("channel4"),
            channel5=data.get("channel5"),
            channel6=data.get("channel6"),
            channel7=data.get("channel7"),
            channel8=data.get("channel8"),
            near=data.get("near"),
            clear=data.get("clear"),
            flicker=data.get("flicker"),
            par=data.get("par"),
            gain=data.get("gain"),
            tint=data.get("tint"),
            light_calculation_reading=data.get("lightCalculationReading"),
        )


@dataclass
class SensorDataPointValue:
    """Represents a single parameter value from a sensor reading."""

    param_name: str
    param_value: str
    measuring_unit: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SensorDataPointValue:
        """Create a SensorDataPointValue from API response data."""
        return cls(
            param_name=data["ParamName"],
            param_value=data["ParamValue"],
            measuring_unit=data.get("MeasuringUnit", ""),
        )


@dataclass
class SensorDataPoint:
    """Represents a sensor data point (UniversalDataPointDto).

    Based on OpenAPI spec, required fields are: sensorId, createdAt
    """

    sensor_id: int
    created_at: datetime
    data_point_values: list[SensorDataPointValue] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SensorDataPoint:
        """Create a SensorDataPoint from API response data."""
        created_at = _parse_datetime(data.get("createdAt"))
        if created_at is None:
            raise ValueError("createdAt is required for SensorDataPoint")

        values = [SensorDataPointValue.from_dict(v) for v in data.get("dataPointValues", [])]
        return cls(
            sensor_id=data["sensorId"],
            created_at=created_at,
            data_point_values=values,
        )


@dataclass
class DeviceData:
    """Container for all devices and sensors."""

    devices: list[Device]
    sensors: list[Sensor]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DeviceData:
        """Create DeviceData from API response."""
        return cls(
            devices=[Device.from_dict(d) for d in data.get("deviceViewDtos", [])],
            sensors=[Sensor.from_dict(s) for s in data.get("universalSensorViews", [])],
        )


@dataclass
class SensorDetails:
    """Detailed sensor information (SensorDeviceDetailsDto).

    Based on OpenAPI spec, required fields are:
    id, sensorType, growId, hubId, hidden, dayStart, nightStart
    """

    # Required fields per OpenAPI spec
    id: int
    sensor_type: int
    grow_id: int
    hub_id: int
    hidden: bool
    day_start: str
    night_start: str

    # Optional fields per OpenAPI spec
    name: str | None = None
    hub_name: str | None = None
    vpd_target: float | None = None
    vpd_leaf_temperature_offset_in_f: float | None = None
    orp_calibration_offset: int | None = None
    sensor_template_id: int | None = None
    sensor_template_name: str | None = None
    offset_id: int | None = None
    par_sensor_subtype: int | None = None

    # Thresholds list
    thresholds: list[dict[str, Any]] = field(default_factory=list)

    # Calibration info (optional)
    ph10_sensor_calibration_info: dict[str, Any] | None = None
    ec1_sensor_calibration_info: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SensorDetails:
        """Create SensorDetails from API response data."""
        return cls(
            id=data["id"],
            sensor_type=data["sensorType"],
            grow_id=data["growId"],
            hub_id=data["hubId"],
            hidden=data["hidden"],
            day_start=data["dayStart"],
            night_start=data["nightStart"],
            name=data.get("name"),
            hub_name=data.get("hubName"),
            vpd_target=data.get("vpdTarget"),
            vpd_leaf_temperature_offset_in_f=data.get("vpdLeafTemperatureOffsetinF"),
            orp_calibration_offset=data.get("orpCalibrationOffSet"),
            sensor_template_id=data.get("sensorTemplateId"),
            sensor_template_name=data.get("sensorTemplateName"),
            offset_id=data.get("offsetId"),
            par_sensor_subtype=data.get("parSensorSubtype"),
            thresholds=data.get("thresholds", []),
            ph10_sensor_calibration_info=data.get("ph10SensorCalibrationInformationDto"),
            ec1_sensor_calibration_info=data.get("ec1SensorCalibrationInformationDto"),
        )


@dataclass
class Hub:
    """Represents a Pulsegrow hub (HubDetailsDto).

    Based on OpenAPI spec, required fields are: id, growId, hidden
    """

    # Required fields per OpenAPI spec
    id: int
    grow_id: int
    hidden: bool

    # Optional fields per OpenAPI spec
    name: str | None = None
    mac_address: str | None = None

    # Lists (may be empty)
    hub_thresholds: list[dict[str, Any]] = field(default_factory=list)
    sensor_devices: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Hub:
        """Create a Hub from API response data."""
        return cls(
            id=data["id"],
            grow_id=data["growId"],
            hidden=data["hidden"],
            name=data.get("name"),
            mac_address=data.get("macAddress"),
            hub_thresholds=data.get("hubThresholds", []),
            sensor_devices=data.get("sensorDevices", []),
        )


@dataclass
class LightReading:
    """Light spectrum reading from Pro device (ProLightReadingDto).

    Based on OpenAPI spec, required fields are:
    deviceId, id, createdAt, channel1-8, ir, clear, flicker, gain, tint, ppfd
    """

    # Required fields per OpenAPI spec
    device_id: int
    id: int
    created_at: datetime
    ppfd: float
    channel1: float
    channel2: float
    channel3: float
    channel4: float
    channel5: float
    channel6: float
    channel7: float
    channel8: float
    ir: float
    clear: float
    flicker: float
    gain: int
    tint: float

    # Optional fields per OpenAPI spec
    note: str | None = None
    dli: float | None = None
    pfd_red: float | None = None
    pfd_green: float | None = None
    pfd_blue: float | None = None
    pfd_ir: float | None = None
    spectrum: list[float] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LightReading:
        """Create a LightReading from API response data."""
        created_at = _parse_datetime(data.get("createdAt"))
        if created_at is None:
            raise ValueError("createdAt is required for LightReading")

        return cls(
            device_id=data["deviceId"],
            id=data["id"],
            created_at=created_at,
            ppfd=data["ppfd"],
            channel1=data["channel1"],
            channel2=data["channel2"],
            channel3=data["channel3"],
            channel4=data["channel4"],
            channel5=data["channel5"],
            channel6=data["channel6"],
            channel7=data["channel7"],
            channel8=data["channel8"],
            ir=data["ir"],
            clear=data["clear"],
            flicker=data["flicker"],
            gain=data["gain"],
            tint=data["tint"],
            note=data.get("note"),
            dli=data.get("dli"),
            pfd_red=data.get("pfdRed"),
            pfd_green=data.get("pfdGreen"),
            pfd_blue=data.get("pfdBlue"),
            pfd_ir=data.get("pfdIr"),
            spectrum=data.get("spectrum", []),
        )


@dataclass
class LightReadingsResponse:
    """Response containing multiple light readings."""

    current_page: int
    total_pages: int
    light_readings: list[LightReading]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LightReadingsResponse:
        """Create LightReadingsResponse from API response data."""
        readings_data = data.get("lightReadings", [])
        return cls(
            current_page=data["currentPage"],
            total_pages=data["totalPages"],
            light_readings=[LightReading.from_dict(r) for r in readings_data],
        )


@dataclass
class TimelineEvent:
    """Represents a timeline event (TimelineEventDto).

    Based on OpenAPI spec, required fields are: timelineEventType, display
    """

    # Required fields per OpenAPI spec
    timeline_event_type: int
    display: bool

    # Optional fields per OpenAPI spec
    id: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None
    title: str | None = None
    detail: str | None = None
    grow_id: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TimelineEvent:
        """Create a TimelineEvent from API response data."""
        return cls(
            timeline_event_type=data["timelineEventType"],
            display=data["display"],
            id=data.get("id", 0),
            created_at=_parse_datetime(data.get("createdAt")),
            updated_at=_parse_datetime(data.get("updatedAt")),
            title=data.get("title"),
            detail=data.get("detail"),
            grow_id=data.get("growId"),
        )


@dataclass
class TriggeredThreshold:
    """Represents a triggered threshold (ViewTriggeredThresholdDto).

    Based on OpenAPI spec, required fields are:
    createdAt, resolved, thresholdType, deviceId, lowOrHigh
    """

    # Required fields per OpenAPI spec
    created_at: datetime
    resolved: bool
    threshold_type: int
    device_id: int
    low_or_high: bool

    # Optional fields per OpenAPI spec
    id: int = 0
    resolved_at: datetime | None = None
    threshold_id: int | None = None
    device_name: str | None = None
    low_threshold_value: float | None = None
    high_threshold_value: float | None = None
    triggering_value: str | None = None
    sensor_threshold_type: int | None = None
    hub_threshold_type: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TriggeredThreshold:
        """Create a TriggeredThreshold from API response data."""
        created_at = _parse_datetime(data.get("createdAt"))
        if created_at is None:
            raise ValueError("createdAt is required for TriggeredThreshold")

        return cls(
            created_at=created_at,
            resolved=data["resolved"],
            threshold_type=data["thresholdType"],
            device_id=data["deviceId"],
            low_or_high=data["lowOrHigh"],
            id=data.get("id", 0),
            resolved_at=_parse_datetime(data.get("resolvedAt")),
            threshold_id=data.get("thresholdId"),
            device_name=data.get("deviceName"),
            low_threshold_value=data.get("lowThresholdValue"),
            high_threshold_value=data.get("highThresholdValue"),
            triggering_value=data.get("triggeringValue"),
            sensor_threshold_type=data.get("sensorThresholdType"),
            hub_threshold_type=data.get("hubThresholdType"),
        )


@dataclass
class UserUsage:
    """User information (UserUsageInformation).

    Based on OpenAPI spec, required fields are: userId
    """

    # Required fields per OpenAPI spec
    user_id: int

    # Optional fields per OpenAPI spec
    user_email: str | None = None
    user_name: str | None = None
    last_active: datetime | None = None
    role: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UserUsage:
        """Create UserUsage from API response data."""
        return cls(
            user_id=data["userId"],
            user_email=data.get("userEmail"),
            user_name=data.get("userName"),
            last_active=_parse_datetime(data.get("lastActive")),
            role=data.get("role"),
        )


@dataclass
class Invitation:
    """Pending invitation information."""

    id: int
    email: str | None = None
    invited_at: datetime | None = None
    invited_by: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Invitation:
        """Create Invitation from API response data."""
        return cls(
            id=data["id"],
            email=data.get("email"),
            invited_at=_parse_datetime(data.get("invitedAt")),
            invited_by=data.get("invitedBy"),
        )


def _parse_datetime(value: str | None) -> datetime | None:
    """Parse ISO 8601 datetime string."""
    if not value:
        return None
    try:
        # Handle various ISO 8601 formats
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None
