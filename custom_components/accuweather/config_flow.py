"""Config flow for AccuWeather Daily Forecast integration."""
import voluptuous as vol
from typing import Any

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_API_KEY
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_LOCATION_KEY, API_ENDPOINT

class AccuWeatherForecastConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AccuWeather Daily Forecast."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> dict[str, Any]:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate the user input
            session = async_get_clientsession(self.hass)
            api_key = user_input[CONF_API_KEY]
            location_key = user_input[CONF_LOCATION_KEY]
            
            url = API_ENDPOINT.format(location_key=location_key)
            params = {
                "apikey": api_key,
                "details": "true",
                "metric": "true",
            }
            
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        # Set unique ID to prevent multiple entries for the same location
                        await self.async_set_unique_id(location_key)
                        self._abort_if_unique_id_configured()

                        return self.async_create_entry(
                            title=f"AccuWeather {location_key}", data=user_input
                        )
                    if response.status in [401, 403]:
                        errors["base"] = "invalid_auth"
                    elif response.status == 404:
                         errors["base"] = "invalid_location"
                    else:
                        errors["base"] = "cannot_connect"

            except Exception:
                errors["base"] = "cannot_connect"

        # Show the form to the user
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): cv.string,
                    vol.Required(CONF_LOCATION_KEY, default="326257"): cv.string,
                }
            ),
            errors=errors,
        )
