"""DataUpdateCoordinator for the AccuWeather Daily Forecast integration."""
import logging
from async_timeout import timeout

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, API_ENDPOINT, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class AccuWeatherForecastCoordinator(DataUpdateCoordinator):
    """Class to manage fetching AccuWeather data."""

    def __init__(self, hass, api_key: str, location_key: str):
        """Initialize the data coordinator."""
        self.api_key = api_key
        self.location_key = location_key
        self.session = async_get_clientsession(hass)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self):
        """Fetch data from AccuWeather API."""
        url = API_ENDPOINT.format(location_key=self.location_key)
        params = {
            "apikey": self.api_key,
            "details": "true",
            "metric": "true",
        }
        
        try:
            async with timeout(15):
                response = await self.session.get(url, params=params)
                if response.status != 200:
                    raise UpdateFailed(f"Error communicating with API: {response.status}")
                
                data = await response.json()
                if not data or "DailyForecasts" not in data or not data["DailyForecasts"]:
                    raise UpdateFailed("Invalid data received from AccuWeather API")
                
                return data

        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
