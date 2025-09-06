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
        # For each day, add the Day and Night phrase sensors
        sensors.append(LongPhraseSensor(coordinator, day_index, "Day"))
        sensors.append(LongPhraseSensor(coordinator, day_index, "Night"))
        
        # And now add the new RealFeel Temperature Max sensor
        sensors.append(RealFeelTempMaxSensor(coordinator, day_index))
        
    async_add_entities(sensors)


class LongPhraseSensor(CoordinatorEntity, SensorEntity):
    """A sensor for one day's LongPhrase (for Day or Night)."""

    def __init__(self, coordinator: MyAccuweatherCoordinator, day_index: int, phrase_type: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.day_index = day_index
        self.phrase_type = phrase_type
        self._location_key = coordinator.location_key

        self._attr_name = f"Forecast Day {self.day_index} {self.phrase_type} Long Phrase"
        self._attr_unique_id = f"{self._location_key}_long_phrase_{self.phrase_type.lower()}_day_{self.day_index}"
        
        if self.phrase_type == "Day":
            self._attr_icon = "mdi:weather-sunny"
        else:
            self._attr_icon = "mdi:weather-night"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data and len(self.coordinator.data) > self.day_index:
            return self.coordinator.data[self.day_index][self.phrase_type]["LongPhrase"]
        return None


class RealFeelTempMaxSensor(CoordinatorEntity, SensorEntity):
    """A sensor for one day's maximum RealFeel temperature."""

    # These attributes tell Home Assistant that this is a temperature sensor.
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:thermometer"

    def __init__(self, coordinator: MyAccuweatherCoordinator, day_index: int):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.day_index = day_index
        self._location_key = coordinator.location_key

        self._attr_name = f"Forecast Day {self.day_index} RealFeel Temp Max"
        self._attr_unique_id = f"{self._location_key}_realfeel_temp_max_day_{self.day_index}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        # Access the correct nested value from the API response
        if self.coordinator.data and len(self.coordinator.data) > self.day_index:
            return self.coordinator.data[self.day_index]["RealFeelTemperature"]["Maximum"]["Value"]
        return None

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        # Dynamically get the unit from the API response to be safe
        if self.coordinator.data and len(self.coordinator.data) > self.day_index:
            unit = self.coordinator.data[self.day_index]["RealFeelTemperature"]["Maximum"]["Unit"]
            if unit == "C":
                return UnitOfTemperature.CELSIUS
            elif unit == "F":
                return UnitOfTemperature.FAHRENHEIT
        return None # Let Home Assistant handle it if data is not available
