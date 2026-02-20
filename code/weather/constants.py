"""
Weather API constants and configuration values.
"""

URL = "https://historical-forecast-api.open-meteo.com/v1/forecast"

# Variables requested hourly
HOURLY_VARIABLES = [
    "apparent_temperature",
    "rain",
    "showers",
    "snowfall",
    "snow_depth",
    "wind_speed_10m",
    "weather_code",
]

# Variables requested daily
DAILY_VARIABLES = [
    "weather_code",
    "sunrise",
    "sunset",
    "daylight_duration",
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "apparent_temperature_mean",
    "rain_sum",
    "showers_sum",
    "snowfall_sum",
    "precipitation_hours",
]

# Weather code mapping
WEATHER_CODES = {
	"0": "Clear sky",
	"1": "Mainly clear",
	"2": "Partly cloudy",
	"3": "Overcast",
	"45": "Fog",
	"48": "Depositing rime fog",
	"51": "Light drizzle",
	"53": "Moderate drizzle",
	"55": "Dense drizzle",
	"56": "Light freezing drizzle",
	"57": "Heavy freezing drizzle",
	"61": "Slight rain",
	"63": "Moderate rain",
	"65": "Heavy rain",
	"66": "Light freezing rain",
	"67": "Heavy freezing rain",
	"71": "Slight snow fall",
	"73": "Moderate snow fall",
	"75": "Heavy snow fall",
	"77": "Snow grains",
	"80": "Slight rain shower",
	"81": "Moderate rain shower",
	"82": "Heavy rain shower",
	"85": "Light snow shower",
	"86": "Heavy snow shower",
	"95": "Slight or moderate thunderstorm",
	"96": "Thunderstorm with slight hail",
	"99": "Thunderstorm with heavy hail",
}