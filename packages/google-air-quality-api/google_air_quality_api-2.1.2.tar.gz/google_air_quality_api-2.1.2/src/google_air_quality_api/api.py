"""API for Google Air Quality bound to Home Assistant OAuth."""

from datetime import UTC, datetime, timedelta

from .auth import Auth
from .exceptions import InvalidCustomLAQIConfigurationError
from .model import AirQualityCurrentConditionsData, AirQualityForecastData

INVALID_CUSTOM_AQI_COMBINATION = (
    "Both region_code and custom_local_aqi must be provided together, or neither."
)


class GoogleAirQualityApi:
    """The Google Air Quality library api client."""

    def __init__(self, auth: Auth) -> None:
        """Initialize GoogleAirQualityApi."""
        self._auth = auth

    async def async_get_current_conditions(
        self,
        lat: float,
        lon: float,
        region_code: str | None = None,
        custom_local_aqi: str | None = None,
    ) -> AirQualityCurrentConditionsData:
        """Get all air quality data."""
        payload = {
            "location": {"latitude": lat, "longitude": lon},
            "extraComputations": [
                "LOCAL_AQI",
                "POLLUTANT_CONCENTRATION",
            ],
            "universalAqi": True,
        }
        if (region_code is None) ^ (custom_local_aqi is None):
            raise InvalidCustomLAQIConfigurationError(INVALID_CUSTOM_AQI_COMBINATION)
        if region_code and custom_local_aqi:
            payload["customLocalAqis"] = [
                {"regionCode": region_code, "aqi": custom_local_aqi}
            ]
        return await self._auth.post_json(
            "currentConditions:lookup",
            json=payload,
            data_cls=AirQualityCurrentConditionsData,
        )

    async def async_get_forecast(
        self, lat: float, lon: float, forecast_timedelta: timedelta
    ) -> AirQualityForecastData:
        """Get air quality forecast data."""
        forecast_date_time = datetime.now(tz=UTC) + forecast_timedelta
        payload = {
            "location": {"latitude": lat, "longitude": lon},
            "extraComputations": [
                "LOCAL_AQI",
                "POLLUTANT_CONCENTRATION",
            ],
            "universalAqi": True,
            "dateTime": forecast_date_time.isoformat(),
        }
        return await self._auth.post_json(
            "forecast:lookup", json=payload, data_cls=AirQualityForecastData
        )
