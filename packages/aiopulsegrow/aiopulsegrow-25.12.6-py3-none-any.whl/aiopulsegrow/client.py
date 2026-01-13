"""Async client for Pulsegrow API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import aiohttp

from .exceptions import (
    PulsegrowAuthError,
    PulsegrowConnectionError,
    PulsegrowError,
    PulsegrowRateLimitError,
)
from .models import (
    Device,
    DeviceData,
    DeviceDataPoint,
    Hub,
    Invitation,
    LightReadingsResponse,
    SensorDataPoint,
    SensorDetails,
    TimelineEvent,
    TriggeredThreshold,
    UserUsage,
)

API_BASE_URL = "https://api.pulsegrow.com"
DEFAULT_TIMEOUT = 10


class PulsegrowClient:
    """Async client for Pulsegrow API.

    This client follows Home Assistant best practices:
    - Accepts an external aiohttp session
    - Manages session lifecycle properly
    - Provides async context manager support
    - Raises specific exceptions for error handling
    """

    def __init__(
        self,
        api_key: str,
        session: aiohttp.ClientSession | None = None,
        base_url: str = API_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the Pulsegrow client.

        Args:
            api_key: Pulsegrow API key for authentication
            session: Optional aiohttp ClientSession. If not provided,
                one will be created.
            base_url: Base URL for API (default: https://api.pulsegrow.com)
            timeout: Request timeout in seconds (default: 10)
        """
        self.api_key = api_key
        self._session = session
        self._close_session = False
        self.base_url = base_url.rstrip("/")
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    async def __aenter__(self) -> PulsegrowClient:
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the client session if it was created internally."""
        if self._close_session and self._session:
            await self._session.close()
            self._session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session.

        Returns:
            aiohttp ClientSession
        """
        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._close_session = True
        return self._session

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Make an API request.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            Response data as dict or list

        Raises:
            PulsegrowAuthError: Authentication failed
            PulsegrowRateLimitError: Rate limit exceeded
            PulsegrowConnectionError: Connection failed
            PulsegrowError: Other API errors
        """
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        headers = {"x-api-key": self.api_key}

        # Clean up None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        try:
            async with session.request(
                method,
                url,
                headers=headers,
                params=params,
                timeout=self.timeout,
            ) as response:
                # Handle error responses
                if response.status == 401:
                    raise PulsegrowAuthError("Authentication failed - invalid API key")
                if response.status == 429:
                    raise PulsegrowRateLimitError("Rate limit exceeded")
                if response.status == 400:
                    error_text = await response.text()
                    raise PulsegrowError(f"Bad request: {error_text}")
                if response.status >= 400:
                    error_text = await response.text()
                    raise PulsegrowError(f"API error {response.status}: {error_text}")

                return await response.json()

        except aiohttp.ClientError as err:
            raise PulsegrowConnectionError(f"Connection error: {err}") from err
        except TimeoutError as err:
            raise PulsegrowConnectionError(f"Request timeout: {err}") from err

    # Device endpoints

    async def get_all_devices(self) -> DeviceData:
        """Get all devices with latest data (excludes sparklines).

        Returns:
            DeviceData object containing devices and sensors
        """
        data = await self._request("GET", "/all-devices")
        return DeviceData.from_dict(data)

    async def get_device_ids(self) -> list[int]:
        """Get list of all device IDs.

        Returns:
            List of device IDs
        """
        return await self._request("GET", "/devices/ids")

    async def get_device_details(self) -> list[Device]:
        """Get comprehensive device information for all devices.

        Returns:
            List of Device objects with detailed information
        """
        data = await self._request("GET", "/devices/details")
        return [Device.from_dict(d) for d in data]

    async def get_device_recent_data(self, device_id: int) -> DeviceDataPoint:
        """Get the last data point for a device.

        Args:
            device_id: Device identifier

        Returns:
            Most recent DeviceDataPoint with all sensor readings
        """
        data = await self._request("GET", f"/devices/{device_id}/recent-data")
        return DeviceDataPoint.from_dict(data)

    async def get_device_data_range(
        self,
        device_id: int,
        start: datetime,
        end: datetime | None = None,
    ) -> list[DeviceDataPoint]:
        """Get device datapoints within specified timeframe.

        Args:
            device_id: Device identifier
            start: Start datetime (ISO 8601)
            end: Optional end datetime (ISO 8601)

        Returns:
            List of DeviceDataPoint objects with all sensor readings
        """
        params = {
            "start": start.isoformat(),
            "end": end.isoformat() if end else None,
        }
        data = await self._request("GET", f"/devices/{device_id}/data-range", params)
        return [DeviceDataPoint.from_dict(d) for d in data]

    async def get_devices_range(
        self,
        start: datetime,
        end: datetime | None = None,
    ) -> list[DeviceDataPoint]:
        """Get all device data within timespan (max 7 days).

        Args:
            start: Start datetime (ISO 8601)
            end: Optional end datetime (ISO 8601)

        Returns:
            List of DeviceDataPoint objects for all devices with all sensor readings
        """
        params = {
            "start": start.isoformat(),
            "end": end.isoformat() if end else None,
        }
        data = await self._request("GET", "/devices/range", params)
        return [DeviceDataPoint.from_dict(d) for d in data]

    # Sensor endpoints

    async def get_sensor_ids(self) -> list[int]:
        """Get list of all sensor IDs.

        Returns:
            List of sensor IDs
        """
        return await self._request("GET", "/sensors/ids")

    async def get_sensor_recent_data(self, sensor_id: int) -> SensorDataPoint:
        """Get the last data point for a sensor.

        Args:
            sensor_id: Sensor identifier

        Returns:
            Most recent SensorDataPoint with parameter values
        """
        data = await self._request("GET", f"/sensors/{sensor_id}/recent-data")
        # API returns MostRecentSensorDataPointDto with dataPointDto nested
        return SensorDataPoint.from_dict(data["dataPointDto"])

    async def force_sensor_read(self, sensor_id: int) -> SensorDataPoint:
        """Trigger immediate sensor measurement.

        Args:
            sensor_id: Sensor identifier

        Returns:
            SensorDataPoint from forced reading with parameter values
        """
        data = await self._request("GET", f"/sensors/{sensor_id}/force-read")
        return SensorDataPoint.from_dict(data)

    async def get_sensor_data_range(
        self,
        sensor_id: int,
        start: datetime,
        end: datetime | None = None,
    ) -> list[SensorDataPoint]:
        """Get sensor datapoints within timeframe.

        Args:
            sensor_id: Sensor identifier
            start: Start datetime (ISO 8601)
            end: Optional end datetime (ISO 8601)

        Returns:
            List of SensorDataPoint objects with parameter values
        """
        params = {
            "start": start.isoformat(),
            "end": end.isoformat() if end else None,
        }
        data = await self._request("GET", f"/sensors/{sensor_id}/data-range", params)
        return [SensorDataPoint.from_dict(d) for d in data]

    async def get_sensor_details(self, sensor_id: int) -> list[SensorDetails]:
        """Get sensor configuration and thresholds.

        Args:
            sensor_id: Sensor identifier

        Returns:
            List of SensorDetails objects
        """
        data = await self._request("GET", f"/sensors/{sensor_id}/details")
        return [SensorDetails.from_dict(d) for d in data]

    # Hub endpoints

    async def get_hub_ids(self) -> list[int]:
        """Get list of all hub IDs.

        Returns:
            List of hub IDs
        """
        return await self._request("GET", "/hubs/ids")

    async def get_hub_details(self, hub_id: int) -> Hub:
        """Get details for a hub.

        Args:
            hub_id: Hub identifier

        Returns:
            Hub object with details
        """
        data = await self._request("GET", f"/hubs/{hub_id}")
        return Hub.from_dict(data)

    # Light reading endpoints (Pro)

    async def get_light_readings(
        self,
        device_id: int,
        page: int | None = None,
    ) -> LightReadingsResponse:
        """Get light readings including spectrum for a device (Pro feature).

        Args:
            device_id: Device identifier
            page: Optional page number (starts at 0)

        Returns:
            LightReadingsResponse object
        """
        params = {"page": page} if page is not None else None
        data = await self._request("GET", f"/api/light-readings/{device_id}", params)
        return LightReadingsResponse.from_dict(data)

    async def trigger_light_reading(self, device_id: int) -> dict[str, Any]:
        """Remotely initiate Pro light measurement.

        Note: Fetch results after 5-10 seconds using get_light_readings.

        Args:
            device_id: Device identifier

        Returns:
            Action result (raw dict as API doesn't specify structure)
        """
        return await self._request("GET", f"/api/devices/{device_id}/trigger-light-reading")

    # Timeline & threshold endpoints

    async def get_timeline(
        self,
        event_types: list[str] | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        count: int | None = None,
        page: int | None = None,
    ) -> list[TimelineEvent]:
        """Get grow events with optional filtering.

        Args:
            event_types: Optional list of event type filters
            start_date: Optional start datetime (defaults to 30 days prior)
            end_date: Optional end datetime
            count: Optional result count limit
            page: Optional page number

        Returns:
            List of TimelineEvent objects
        """
        params: dict[str, Any] = {
            "startDate": start_date.isoformat() if start_date else None,
            "endDate": end_date.isoformat() if end_date else None,
            "count": count,
            "page": page,
        }
        if event_types:
            # Convert list to multiple query parameters
            for event_type in event_types:
                if "eventTypes" not in params:
                    params["eventTypes"] = []
                params["eventTypes"].append(event_type)

        data = await self._request("GET", "/api/timeline", params)
        return [TimelineEvent.from_dict(e) for e in data]

    async def get_triggered_thresholds(self) -> list[TriggeredThreshold]:
        """Get active and resolved threshold violations.

        Returns:
            List of TriggeredThreshold objects
        """
        data = await self._request("GET", "/api/triggered-thresholds")
        return [TriggeredThreshold.from_dict(t) for t in data]

    # User endpoints

    async def get_users(self) -> list[UserUsage]:
        """Get user usage information for API key.

        Returns:
            List of UserUsage objects
        """
        data = await self._request("GET", "/users")
        return [UserUsage.from_dict(u) for u in data]

    async def get_invitations(self) -> list[Invitation]:
        """Get pending invitations that haven't been accepted or canceled.

        Returns:
            List of Invitation objects
        """
        data = await self._request("GET", "/invitations")
        return [Invitation.from_dict(i) for i in data]
