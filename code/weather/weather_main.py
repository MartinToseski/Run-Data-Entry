import numpy as np
import requests_cache
import openmeteo_requests
from datetime import datetime
from retry_requests import retry
from code.garmin.utils import get_today_date
from code.garmin.extract import extract_today_run_stats, extract_location_stats
from code.garmin.example import init_api


# Set up the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://historical-forecast-api.open-meteo.com/v1/forecast"

weather_code = {
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

def get_hourly_data(params, responses, hour):
	# Process first location. Add a for-loop for multiple locations or weather models
	response = responses[0]

	# Process hourly data. The order of variables needs to be the same as requested.
	hourly = response.Hourly()

	if hour:
		return {
			"hourly_apparent_temperature": round(hourly.Variables(0).ValuesAsNumpy().astype(float)[hour]),
			"hourly_rain_mm": round(hourly.Variables(1).ValuesAsNumpy().astype(float)[hour].item(), 1),
			"hourly_showers_mm": round(hourly.Variables(2).ValuesAsNumpy().astype(float)[hour].item(), 1),
			"hourly_snowfall_mm": round(hourly.Variables(3).ValuesAsNumpy().astype(float)[hour].item(), 1),
			"hourly_snow_depth_cm": round(hourly.Variables(4).ValuesAsNumpy().astype(float)[hour].item(), 1),
			"hourly_wind_speed_10m_kmh": round(hourly.Variables(5).ValuesAsNumpy().astype(float)[hour].item(), 1),
			"hourly_weather_code": hourly.Variables(6).ValuesAsNumpy().astype(int)[hour].item()
		}
	else:
		return {
			"hourly_apparent_temperature": round(np.median(hourly.Variables(0).ValuesAsNumpy().astype(float))),
			"hourly_rain_mm": round(np.median(hourly.Variables(1).ValuesAsNumpy().astype(float)).item(), 1),
			"hourly_showers_mm": round(np.median(hourly.Variables(2).ValuesAsNumpy().astype(float)).item(), 1),
			"hourly_snowfall_mm": round(np.median(hourly.Variables(3).ValuesAsNumpy().astype(float)).item(), 1),
			"hourly_snow_depth_cm": round(np.median(hourly.Variables(4).ValuesAsNumpy().astype(float)).item(), 1),
			"hourly_wind_speed_10m_kmh": round(np.median(hourly.Variables(5).ValuesAsNumpy().astype(float)).item(), 1),
			"hourly_weather_code": round(np.median(hourly.Variables(6).ValuesAsNumpy().astype(int)).item()),
		}


def get_daily_data(parameters, responses):
	response = responses[0]
	# Process daily data. The order of variables needs to be the same as requested.
	daily = response.Daily()

	return {
		"daily_weather_code": daily.Variables(0).ValuesAsNumpy().astype(int)[0].item() ,
		"daily_sunrise": datetime.fromtimestamp(daily.Variables(1).ValuesInt64AsNumpy().astype(int)[0].item()).strftime("%H:%M:%S"),
		"daily_sunset": datetime.fromtimestamp(daily.Variables(2).ValuesInt64AsNumpy().astype(int)[0].item()).strftime("%H:%M:%S"),
		"daily_daylight_duration": int(daily.Variables(3).ValuesAsNumpy().astype(float)[0].item() // 3600),
		"daily_temperature_2m_max": round(daily.Variables(4).ValuesAsNumpy().astype(float)[0].item()),
		"daily_temperature_2m_min": round(daily.Variables(5).ValuesAsNumpy().astype(float)[0].item()),
		"daily_temperature_2m_mean": round(daily.Variables(6).ValuesAsNumpy().astype(float)[0].item()),
		"daily_apparent_temperature_mean": round(daily.Variables(7).ValuesAsNumpy().astype(float)[0].item()),
		"daily_rain_sum": round(daily.Variables(8).ValuesAsNumpy().astype(float)[0].item(), 1),
		"daily_showers_sum": round(daily.Variables(9).ValuesAsNumpy().astype(float)[0].item(), 1),
		"daily_snowfall_sum": round(daily.Variables(10).ValuesAsNumpy().astype(float)[0].item(), 1),
		"daily_precipitation_hours": round(daily.Variables(11).ValuesAsNumpy().astype(float)[0].item()),
	}


def main():
	garmin_api = init_api()
	recent_garmin_location_stats = extract_location_stats(garmin_api)
	coords = recent_garmin_location_stats["location_coordinates"]

	today_run_garmin_stats = extract_today_run_stats(garmin_api)
	run_today_start_time = today_run_garmin_stats["run_today_start_time"]
	run_today_hour = int(run_today_start_time.split(":")[0])

	hourly_data = ["apparent_temperature", "rain", "showers", "snowfall", "snow_depth", "wind_speed_10m", "weather_code"]
	daily_data = ["weather_code", "sunrise", "sunset", "daylight_duration", "temperature_2m_max", "temperature_2m_min",
					  "temperature_2m_mean", "apparent_temperature_mean", "rain_sum", "showers_sum", "snowfall_sum",
					  "precipitation_hours"]

	params = {
		"latitude": coords[0],
		"longitude": coords[1],
		"start_date": get_today_date(),
		"end_date": get_today_date(),
		"hourly": hourly_data,
		"daily": daily_data,
    	"timezone": "auto"
	}
	responses = openmeteo.weather_api(url, params=params)

	print(get_hourly_data(params, responses, None))
	print()
	print(get_daily_data(params, responses))


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("Exiting...")
	except Exception as e:
		print(e)
