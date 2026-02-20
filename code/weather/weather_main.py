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

from code.garmin.utils import get_today_date
from code.garmin.extract import extract_today_run_stats, extract_location_stats
from code.garmin.example import init_api

from .client import build_weather_client
from .constants import URL, HOURLY_VARIABLES, DAILY_VARIABLES
from .parsing import extract_hourly_data, extract_daily_data


def main():
	"""
	Main entry point for weather extraction.

	Steps:
	1. Initialize Garmin API and extract location.
	2. Determine current run hour (if a run is happening today).
	3. Build Open-Meteo client and fetch weather.
	4. Extract hourly and daily metrics.
	"""
	garmin_api = init_api()
	garmin_location_stats = extract_location_stats(garmin_api)
	coords = garmin_location_stats.get("location_coordinates")

	if not coords:
		raise ValueError("No location coordinates found")

	run_stats = extract_today_run_stats(garmin_api)
	run_start_time = run_stats.get("run_today_start_time")
	run_start_hour = int(run_start_time.split(":")[0]) if run_start_time else None

	client = build_weather_client()

	params = {
		"latitude": coords[0],
		"longitude": coords[1],
		"start_date": get_today_date(),
		"end_date": get_today_date(),
		"hourly": HOURLY_VARIABLES,
		"daily": DAILY_VARIABLES,
    	"timezone": "auto"
	}

	responses = client.weather_api(URL, params=params)

	print(extract_hourly_data(responses[0], run_start_hour))
	print()
	print(extract_daily_data(responses[0]))


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("Exiting...")
	except Exception as e:
		print(e)
