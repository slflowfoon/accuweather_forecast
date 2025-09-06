"""Sensor platform for My AccuWeather Phrases."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature

from .const import DOMAIN
from .coordinator import MyAccuweatherCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Create a list to hold all our new sensors
    sensors = []

    # Loop through each of the 5 days
    for day_index in range(5):
        # For each day, add a sensor for the "Day" phrase, the "Night" phrase,
        # and the Maximum RealFeel Temperature.
        sensors.append(LongPhraseSensor(coordinator, day_index, "Day"))
        sensors.append(LongPhraseSensor(coordinator, day_index, "Night"))
        sensors.append(RealFeelTempMaxSensor(coordinator, day_index))

    async_add_entities(sensors)


class LongPhraseSensor(CoordinatorEntity, SensorEntity):
    """A sensor for one day's LongPhrase (for Day or Night)."""

    def __init__(self, coordinator: MyAccuweatherCoordinator, day_index: int, phrase_type: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.day_index = day_index
        self.phrase_type = phrase_type  # "Day" or "Night"
        self._location_key = coordinator.location_key

        # Set entity attributes dynamically based on phrase_type
        self._attr_name = f"Forecast Day {self.day_index} {self.phrase_type} Long Phrase"
        self._attr_unique_id = f"{self._location_key}_long_phrase_{self.phrase_type.lower()}_day_{self.day_index}"

        # Set a different icon for day and night
        if self.phrase_type == "Day":
            self._attr_icon = "mdi:weather-sunny"
        else:
            self._attr_icon = "mdi:weather-night"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        # Make sure data exists and is a list with enough items
        if self.coordinator.data and len(self.coordinator.data) > self.day_index:
            # Use self.phrase_type to get the correct data ("Day" or "Night")
            return self.coordinator.data[self.day_index][self.phrase_type]["LongPhrase"]
        return None  # Return None if data is not available


class RealFeelTempMaxSensor(CoordinatorEntity, SensorEntity):
    """A sensor for one day's Maximum RealFeel Temperature."""

    # Set Home Assistant sensor properties
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: MyAccuweatherCoordinator, day_index: int):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.day_index = day_index
        self._location_key = coordinator.location_key

        # Set entity attributes
        self._attr_name = f"Forecast Day {self.day_index} RealFeel Temp Max"
        self._attr_unique_id = f"{self._location_key}_realfeel_temp_max_day_{self.day_index}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data and len(self.coordinator.data) > self.day_index:
            try:
                # Navigate to the specific value in the API response
                return self.coordinator.data[self.day_index]["RealFeelTemperature"]["Maximum"]["Value"]
            except (KeyError, IndexError):
                # Data structure is not as expected
                return None
        return None

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        if self.coordinator.data and len(self.coordinator.data) > self.day_index:
            try:
                unit = self.coordinator.data[self.day_index]["RealFeelTemperature"]["Maximum"]["Unit"]
                return UnitOfTemperature.CELSIUS if unit == "C" else UnitOfTemperature.FAHRENHEIT
            except (KeyError, IndexError):
                return None
        return None
