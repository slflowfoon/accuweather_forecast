"""DataUpdateCoordinator for the My AccuWeather Phrases integration."""
from datetime import timedelta
import logging

import httpx

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.const import TEMP_CELSIUS, TEMP_FAHRENHEIT

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class MyAccuweatherCoordinator(DataUpdateCoordinator):
    """My AccuWeather data update coordinator."""

    def __init__(self, hass, api_key: str, location_key: str, is_metric: bool):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=1),
        )
        self.api_key = api_key
        self.location_key = location_key
        self.is_metric = is_metric
        self.temp_unit = TEMP_CELSIUS if is_metric else TEMP_FAHRENHEIT

        # Dynamically build the URL based on the unit system
        self.api_url = (
            "http://dataservice.accuweather.com/forecasts/v1/daily/5day/"
            f"{self.location_key}?apikey={self.api_key}&details=true&metric={str(self.is_metric).lower()}"
        )
        self.async_client = httpx.AsyncClient()

    async def _async_update_data(self):
        """Fetch data from the AccuWeather API."""
        try:
            response = await self.async_client.get(self.api_url)
            response.raise_for_status()
            data = response.json()
            return data["DailyForecasts"]
        except httpx.HTTPStatusError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err
