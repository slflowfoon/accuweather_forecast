"""Constants for the AccuWeather Daily Forecast integration."""
from datetime import timedelta

DOMAIN = "accuweather_forecast"

# Configuration constants
CONF_API_KEY = "api_key"
CONF_LOCATION_KEY = "location_key"

# API
API_ENDPOINT = "http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}"
ATTRIBUTION = "Data provided by AccuWeather"

# Update interval
UPDATE_INTERVAL = timedelta(minutes=60)
