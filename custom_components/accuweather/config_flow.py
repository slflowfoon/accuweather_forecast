"""Config flow for My AccuWeather Phrases."""
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

class MyAccuweatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for My AccuWeather Phrases."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # For simplicity, we don't validate here, but in a real component you would
            # try to connect to the API to make sure the keys are valid.
            return self.async_create_entry(
                title=f"AccuWeather Location {user_input['location_key']}",
                data=user_input
            )

        # This is the form the user will see
        data_schema = vol.Schema({
            vol.Required("api_key"): str,
            vol.Required("location_key", default="326257"): str,
        })

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
