"""Sensor platform for My AccuWeather Phrases."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN
from .coordinator import MyAccuweatherCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Create a sensor for each of the 5 days in the forecast
    sensors = [
        LongPhraseSensor(coordinator, day_index)
        for day_index in range(5)
    ]
    async_add_entities(sensors)


class LongPhraseSensor(CoordinatorEntity, SensorEntity):
    """A sensor for one day's LongPhrase."""

    def __init__(self, coordinator: MyAccuweatherCoordinator, day_index: int):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.day_index = day_index
        self._location_key = coordinator.location_key

        # Set entity attributes
        self._attr_name = f"Forecast Day {self.day_index} Long Phrase"
        self._attr_unique_id = f"{self._location_key}_long_phrase_day_{self.day_index}"
        self._attr_icon = "mdi:text-long"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        # Make sure data exists and is a list with enough items
        if self.coordinator.data and len(self.coordinator.data) > self.day_index:
            return self.coordinator.data[self.day_index]["Day"]["LongPhrase"]
        return None  # Return None if data is not available
