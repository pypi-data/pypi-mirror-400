"""Enumerations and constants for Pulsegrow API.

All enum values are sourced from the official Pulsegrow API specification.
"""

from enum import IntEnum


class DeviceType(IntEnum):
    """Device type identifiers.

    These are the deviceType values returned by the API for different
    device categories.
    """

    PULSE_ONE = 0
    """PulseOne device - Original all-in-one environmental monitoring device"""

    PULSE_PRO = 1
    """PulsePro device - Professional environmental monitoring with advanced light sensors"""

    PULSE_HUB = 2
    """PulseHub - Hub device that connects up to 12 modular sensors"""

    SENSOR = 3
    """Universal sensor device (pH, EC, etc.) connected to a hub"""

    CONTROL = 4
    """Control device (e.g., OpenSprinkler)"""

    PULSE_ZERO = 5
    """PulseZero device - Entry-level environmental monitoring"""


class SensorType(IntEnum):
    """Sensor type identifiers.

    These are the sensorType values returned by the API for different
    sensor models connected to hubs.
    """

    HUB = 0
    """Hub sensor"""

    VWC1 = 1
    """Volumetric Water Content sensor v1"""

    THV1 = 2
    """Temperature/Humidity/VPD sensor v1"""

    PH10 = 3
    """pH sensor model 10"""

    EC1 = 4
    """EC (Electrical Conductivity) sensor v1"""

    VWC12 = 5
    """Volumetric Water Content sensor v12"""

    PAR1 = 8
    """PAR (Photosynthetically Active Radiation) sensor v1"""

    VWC2 = 9
    """Volumetric Water Content sensor v2"""

    ORP1 = 10
    """ORP (Oxidation-Reduction Potential) sensor v1"""

    THC1 = 11
    """Temperature/Humidity/CO2 sensor v1"""

    TDO1 = 12
    """Total Dissolved Oxygen sensor v1"""

    VWC3 = 13
    """Volumetric Water Content sensor v3"""


class TimelineEventType(IntEnum):
    """Timeline event type identifiers.

    These indicate the type of event recorded in the grow timeline.
    """

    NOTE = 1
    """User note/observation"""

    NOTIFICATION = 2
    """System notification (threshold alerts, etc.)"""

    ENVIRONMENT = 3
    """Environmental change event"""

    DEVICE_ADDED = 4
    """New device added to grow"""

    FEEDING = 5
    """Feeding/nutrient event"""

    PESTS = 6
    """Pest observation or treatment"""

    MAINTENANCE_AND_CLEANING = 7
    """Maintenance or cleaning activity"""

    SENSOR_CALIBRATED = 8
    """Sensor calibration event"""

    BATCH_STARTED = 9
    """New grow batch started"""

    BATCH_ZONE_CHANGED = 10
    """Grow zone changed for batch"""


class ThresholdType(IntEnum):
    """Device threshold type identifiers.

    These indicate what type of device threshold was triggered.
    """

    LIGHT = 1
    """Light intensity threshold"""

    TEMPERATURE = 2
    """Temperature threshold"""

    HUMIDITY = 3
    """Humidity threshold"""

    POWER = 4
    """Power/battery threshold"""

    CONNECTIVITY = 5
    """Connectivity/signal threshold"""

    BATTERY_V = 6
    """Battery voltage threshold"""

    CO2 = 7
    """CO2 concentration threshold"""

    VOC = 8
    """VOC (Volatile Organic Compounds) threshold"""

    VPD = 11
    """VPD (Vapor Pressure Deficit) threshold"""

    DEW_POINT = 12
    """Dew point threshold"""

    OUTLET_TO_BATTERY_TRANSITION = 13
    """Outlet to battery power transition"""

    DEW_POINT_DUAL_DIRECTION = 14
    """Dew point threshold (both directions)"""


class SensorThresholdType(IntEnum):
    """Sensor threshold type identifiers.

    These indicate what type of sensor threshold was triggered.
    """

    VWC1 = 1
    """VWC1 sensor volumetric water content threshold"""

    TEMPERATURE = 2
    """Temperature threshold"""

    HUMIDITY = 3
    """Humidity threshold"""

    VPD = 4
    """VPD (Vapor Pressure Deficit) threshold"""

    DEW_POINT = 5
    """Dew point threshold"""

    PH = 6
    """pH threshold"""

    EC1_EC = 7
    """EC1 sensor electrical conductivity threshold"""

    EC1_TEMP = 8
    """EC1 sensor temperature threshold"""

    VWC1_SENSOR_PWEC_THRESHOLD = 9
    """VWC1 sensor pore water EC threshold"""

    VWC12_VWC_THRESHOLD = 10
    """VWC12 sensor volumetric water content threshold"""

    VWC12_SENSOR_PWEC_THRESHOLD = 11
    """VWC12 sensor pore water EC threshold"""

    PAR1_PPFD = 12
    """PAR1 sensor PPFD (Photosynthetic Photon Flux Density) threshold"""

    SUBSTRATE_TEMP = 13
    """Substrate temperature threshold"""

    SUBSTRATE_BULK_EC = 14
    """Substrate bulk EC threshold"""

    PH1_TEMP = 15
    """pH sensor temperature threshold"""

    PAR1_DLI = 16
    """PAR1 sensor DLI (Daily Light Integral) threshold"""

    VWC2_VWC_THRESHOLD = 17
    """VWC2 sensor volumetric water content threshold"""

    VWC2_PWEC_THRESHOLD = 18
    """VWC2 sensor pore water EC threshold"""

    ORP1_ORP = 19
    """ORP1 sensor oxidation-reduction potential threshold"""

    THC1_CO2 = 20
    """THC1 sensor CO2 threshold"""

    THC1_RH = 21
    """THC1 sensor relative humidity threshold"""

    THC1_TEMP = 22
    """THC1 sensor temperature threshold"""

    THC1_DEW_POINT = 23
    """THC1 sensor dew point threshold"""

    THC1_VPD = 24
    """THC1 sensor VPD threshold"""

    TDO1_TEMPERATURE_THRESHOLD = 25
    """TDO1 sensor temperature threshold"""

    TDO1_DO_THRESHOLD = 26
    """TDO1 sensor dissolved oxygen threshold"""

    THC1_LIGHT = 27
    """THC1 sensor light threshold"""


class HubThresholdType(IntEnum):
    """Hub threshold type identifiers.

    These indicate what type of hub threshold was triggered.
    """

    POWER = 1
    """Hub power threshold"""

    CONNECTIVITY = 2
    """Hub connectivity threshold"""


class ParSensorSubtype(IntEnum):
    """PAR sensor subtype identifiers.

    Indicates which PAR sensor model is being used.
    """

    SQ522 = 0
    """Apogee SQ-522 Full-Spectrum Quantum Sensor"""

    SQ618 = 1
    """Apogee SQ-618 Full-Spectrum Quantum Sensor"""


class UserGrowRole(IntEnum):
    """User role identifiers for grow access.

    Defines the permission level for a user in a grow.
    """

    OWNER = 0
    """Grow owner - full access"""

    ADMIN = 1
    """Administrator - full management access"""

    EDITOR = 2
    """Editor - can modify settings and data"""

    VIEWER = 3
    """Viewer - read-only access"""

    INVITED = 4
    """Invited user - pending acceptance"""

    GUEST = 5
    """Guest - limited temporary access"""
