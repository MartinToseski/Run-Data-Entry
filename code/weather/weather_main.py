"""
Weather Data Extraction Entry Point.

This module fetches weather data for the user's running location
using Garmin location stats and the Open-Meteo API. It outputs
hourly and daily weather metrics for the current date.

It relies on:
- Garmin data extraction utils
- Open-Meteo API client with caching and retries
- Parsing helpers for hourly and daily weather data
"""

from typing import Dict, Any
from datetime import date
from code.garmin.extract import extract_today_run_stats, extract_location_stats
from code.garmin.client import init_api
from .client import build_weather_client
from .constants import URL, HOURLY_VARIABLES, DAILY_VARIABLES
from .parsing import extract_hourly_data, extract_daily_data


def extract_weather_data(target_date: date) -> Dict[str, Any]:
	"""
    Main entry point for weather extraction.
    
    Steps:
    1. Initialize Garmin API and extract location.
    2. Determine current run hour (if a run is happening today).
    3. Build Open-Meteo client and fetch weather.
    4. Extract hourly and daily metrics.
    """
	garmin_api = init_api()
	garmin_location_stats = extract_location_stats(garmin_api, target_date)
	coords = garmin_location_stats.get("location_coordinates")

	if not coords:
		return {
			key: None for key in (
				"hourly_apparent_temperature",
				"hourly_rain_mm",
				"hourly_showers_mm",
				"hourly_snowfall_mm",
				"hourly_snow_depth_cm",
				"hourly_wind_speed_10m_kmh",
				"hourly_weather_code",
				"daily_weather_code",
				"daily_sunrise",
				"daily_sunset",
				"daily_daylight_duration",
				"daily_temperature_2m_max",
				"daily_temperature_2m_min",
				"daily_temperature_2m_mean",
				"daily_apparent_temperature_mean",
				"daily_rain_sum",
				"daily_showers_sum",
				"daily_snowfall_sum",
				"daily_precipitation_hours"
			)
		}

	run_stats = extract_today_run_stats(garmin_api, target_date)
	run_start_time = run_stats.get("run_today_start_time")
	run_start_hour = int(run_start_time.split(":")[0]) if run_start_time else None

	client = build_weather_client()

	params = {
		"latitude": coords[0],
		"longitude": coords[1],
		"start_date": target_date.isoformat(),
		"end_date": target_date.isoformat(),
		"hourly": HOURLY_VARIABLES,
		"daily": DAILY_VARIABLES,
		"timezone": "auto"
	}

	responses = client.weather_api(URL, params=params)
	return extract_hourly_data(responses[0], run_start_hour) | extract_daily_data(responses[0])


def main(target_date: date = None):
	try:
		return extract_weather_data(target_date)
	except Exception as e:
		print(e)


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("Exiting Open-Meteo...")
	except Exception as e:
		print("Open-Meteo - ", e)
