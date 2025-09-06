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

    entities = [
        AccuWeatherLongPhraseSensor(coordinator, location_key),
        AccuWeatherRealFeelMaxSensor(coordinator, location_key),
    ]
    async_add_entities(entities)


class AccuWeatherForecastBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for AccuWeather Forecast sensors."""

    def __init__(self, coordinator: AccuWeatherForecastCoordinator, location_key: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._location_key = location_key
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
    def today_forecast(self):
        """Return today's forecast data from the coordinator."""
        # The first item in the list is today's forecast
        if self.coordinator.data and self.coordinator.data.get("DailyForecasts"):
            return self.coordinator.data["DailyForecasts"][0]
        return None

class AccuWeatherLongPhraseSensor(AccuWeatherForecastBaseSensor):
    """Representation of the Long Phrase sensor."""

    _attr_icon = "mdi:text-long"
    
    def __init__(self, coordinator: AccuWeatherForecastCoordinator, location_key: str):
        """Initialize the sensor."""
        super().__init__(coordinator, location_key)
        self._attr_name = f"AccuWeather Day Long Phrase"
        self._attr_unique_id = f"{location_key}_day_long_phrase"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if self.today_forecast:
            try:
                return self.today_forecast["Day"]["LongPhrase"]
            except (KeyError, IndexError):
                return None
        return None


class AccuWeatherRealFeelMaxSensor(AccuWeatherForecastBaseSensor):
    """Representation of the Maximum RealFeel Temperature sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: AccuWeatherForecastCoordinator, location_key: str):
        """Initialize the sensor."""
        super().__init__(coordinator, location_key)
        self._attr_name = f"AccuWeather RealFeel Max"
        self._attr_unique_id = f"{location_key}_realfeel_max"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.today_forecast:
            try:
                return self.today_forecast["RealFeelTemperature"]["Maximum"]["Value"]
            except (KeyError, IndexError):
                return None
        return None
