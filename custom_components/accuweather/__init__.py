"""The My AccuWeather Phrases integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .coordinator import MyAccuweatherCoordinator
from .const import DOMAIN

PLATFORMS = [Platform.SENSOR]

async def async_setup_entry(hass: Home Assistant, entry: ConfigEntry) -> bool:
    """Set up My AccuWeather Phrases from a config entry."""
    api_key = entry.data["api_key"]
    location_key = entry.data["location_key"]
    is_metric = hass.config.units.is_metric

    # Create the coordinator, passing in the unit system
    coordinator = MyAccuweatherCoordinator(hass, api_key, location_key, is_metric)

    # Fetch initial data so we have it when the sensors are set up
    await coordinator.async_config_entry_first_refresh()

    # Store the coordinator in hass.data
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Forward the setup to the sensor platform
    await hass.config.entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config.entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
