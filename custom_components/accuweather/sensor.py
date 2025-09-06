"""Platform for AccuWeather Daily Forecast sensor entities."""
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ATTRIBUTION, CONF_LOCATION_KEY
from .coordinator import AccuWeatherForecastCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: AccuWeatherForecastCoordinator = hass.data[DOMAIN][entry.entry_id]
    location_key = entry.data[CONF_LOCATION_KEY]

    entities = []
    # The API provides 5 days of forecasts, create sensors for each day.
    for day_index in range(5):
        entities.append(AccuWeatherLongPhraseSensor(coordinator, location_key, day_index))
        entities.append(AccuWeatherNightLongPhraseSensor(coordinator, location_key, day_index))
        entities.append(AccuWeatherRealFeelMaxSensor(coordinator, location_key, day_index))
    
    async_add_entities(entities)


class AccuWeatherForecastBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for AccuWeather Forecast sensors."""

    def __init__(self, coordinator: AccuWeatherForecastCoordinator, location_key: str, day_index: int):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._location_key = location_key
        self._day_index = day_index
        self._attr_attribution = ATTRIBUTION

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._location_key)},
            "name": f"AccuWeather Forecast ({self._location_key})",
            "manufacturer": "AccuWeather",
            "entry_type": "service",
        }
    
    @property
    def day_forecast(self):
        """Return the forecast data for the specific day from the coordinator."""
        # Check if data is available and the list is long enough for the index
        if (
            self.coordinator.data
            and self.coordinator.data.get("DailyForecasts")
            and len(self.coordinator.data["DailyForecasts"]) > self._day_index
        ):
            return self.coordinator.data["DailyForecasts"][self._day_index]
        return None

    @property
    def _day_name(self) -> str:
        """Return a friendly name for the day index."""
        # Use the numerical index for all days as requested.
        return f"Day {self._day_index}"


class AccuWeatherLongPhraseSensor(AccuWeatherForecastBaseSensor):
    """Representation of the Day Long Phrase sensor for a specific day."""

    _attr_icon = "mdi:text-long"
    
    def __init__(self, coordinator: AccuWeatherForecastCoordinator, location_key: str, day_index: int):
        """Initialize the sensor."""
        super().__init__(coordinator, location_key, day_index)
        self._attr_name = f"AccuWeather Day Long Phrase {self._day_name}"
        self._attr_unique_id = f"{location_key}_day_long_phrase_{self._day_index}"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if self.day_forecast:
            try:
                return self.day_forecast["Day"]["LongPhrase"]
            except (KeyError, IndexError):
                return None
        return None

class AccuWeatherNightLongPhraseSensor(AccuWeatherForecastBaseSensor):
    """Representation of the Night Long Phrase sensor for a specific day."""

    _attr_icon = "mdi:weather-night"
    
    def __init__(self, coordinator: AccuWeatherForecastCoordinator, location_key: str, day_index: int):
        """Initialize the sensor."""
        super().__init__(coordinator, location_key, day_index)
        self._attr_name = f"AccuWeather Night Long Phrase {self._day_name}"
        self._attr_unique_id = f"{location_key}_night_long_phrase_{self._day_index}"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if self.day_forecast:
            try:
                return self.day_forecast["Night"]["LongPhrase"]
            except (KeyError, IndexError):
                return None
        return None


class AccuWeatherRealFeelMaxSensor(AccuWeatherForecastBaseSensor):
    """Representation of the Maximum RealFeel Temperature sensor for a specific day."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: AccuWeatherForecastCoordinator, location_key: str, day_index: int):
        """Initialize the sensor."""
        super().__init__(coordinator, location_key, day_index)
        self._attr_name = f"AccuWeather RealFeel Max {self._day_name}"
        self._attr_unique_id = f"{location_key}_realfeel_max_{self._day_index}"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.day_forecast:
            try:
                return self.day_forecast["RealFeelTemperature"]["Maximum"]["Value"]
            except (KeyError, IndexError):
                return None
        return None
