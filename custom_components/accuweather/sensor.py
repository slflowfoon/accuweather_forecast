"""Sensor platform for My AccuWeather Phrases."""
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

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
        # For each day, add a sensor for the "Day" phrase AND the "Night" phrase
        sensors.append(LongPhraseSensor(coordinator, day_index, "Day"))
        sensors.append(LongPhraseSensor(coordinator, day_index, "Night"))
        
        # --- ADD THE NEW SENSOR ---
        # For each day, also add a sensor for the RealFeel Max Temperature
        sensors.append(RealFeelMaxSensor(coordinator, day_index))
        
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

# --- NEW SENSOR CLASS ---
class RealFeelMaxSensor(CoordinatorEntity, SensorEntity):
    """A sensor for one day's RealFeel Maximum Temperature."""

    # Set device class and state class for proper handling in Home Assistant
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    
    def __init__(self, coordinator: MyAccuweatherCoordinator, day_index: int):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.day_index = day_index
        self._location_key = coordinator.location_key

        # Set entity attributes
        self._attr_name = f"Forecast Day {self.day_index} RealFeel Max Temp"
        self._attr_unique_id = f"{self._location_key}_realfeel_max_day_{self.day_index}"
        self._attr_icon = "mdi:thermometer"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data and len(self.coordinator.data) > self.day_index:
            # Navigate through the nested dictionary to get the value
            return self.coordinator.data[self.day_index]["RealFeelTemperature"]["Maximum"]["Value"]
        return None

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        if self.coordinator.data and len(self.coordinator.data) > self.day_index:
            unit = self.coordinator.data[self.day_index]["RealFeelTemperature"]["Maximum"]["Unit"]
            return f"°{unit}" # Returns °C or °F
        return None
