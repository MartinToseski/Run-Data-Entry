import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from code.garmin.extract import extract_today_run_stats, extract_location_stats
from code.garmin.example import init_api


# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://historical-forecast-api.open-meteo.com/v1/forecast"


def get_hourly_data(params, responses):
	# Process first location. Add a for-loop for multiple locations or weather models
	response = responses[0]

	# Process hourly data. The order of variables needs to be the same as requested.
	hourly = response.Hourly()
	hourly_apparent_temperature = hourly.Variables(0).ValuesAsNumpy()
	hourly_rain = hourly.Variables(1).ValuesAsNumpy()
	hourly_showers = hourly.Variables(2).ValuesAsNumpy()
	hourly_snowfall = hourly.Variables(3).ValuesAsNumpy()
	hourly_snow_depth = hourly.Variables(4).ValuesAsNumpy()
	hourly_wind_speed_10m = hourly.Variables(5).ValuesAsNumpy()

	hourly_data = {"date": pd.date_range(
		start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
		end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = hourly.Interval()),
		inclusive = "left"
	)}

	hourly_data["apparent_temperature"] = hourly_apparent_temperature
	hourly_data["rain"] = hourly_rain
	hourly_data["showers"] = hourly_showers
	hourly_data["snowfall"] = hourly_snowfall
	hourly_data["snow_depth"] = hourly_snow_depth
	hourly_data["wind_speed_10m"] = hourly_wind_speed_10m

	hourly_dataframe = pd.DataFrame(data = hourly_data)
	return hourly_dataframe


def get_daily_data(parameters, responses):
	response = responses[0]
	# Process daily data. The order of variables needs to be the same as requested.
	daily = response.Daily()
	daily_weather_code = daily.Variables(0).ValuesAsNumpy()
	daily_sunrise = daily.Variables(1).ValuesInt64AsNumpy()
	daily_sunset = daily.Variables(2).ValuesInt64AsNumpy()
	daily_daylight_duration = daily.Variables(3).ValuesAsNumpy()
	daily_temperature_2m_max = daily.Variables(4).ValuesAsNumpy()
	daily_temperature_2m_min = daily.Variables(5).ValuesAsNumpy()
	daily_temperature_2m_mean = daily.Variables(6).ValuesAsNumpy()
	daily_apparent_temperature_mean = daily.Variables(7).ValuesAsNumpy()
	daily_rain_sum = daily.Variables(8).ValuesAsNumpy()
	daily_showers_sum = daily.Variables(9).ValuesAsNumpy()
	daily_snowfall_sum = daily.Variables(10).ValuesAsNumpy()
	daily_precipitation_hours = daily.Variables(11).ValuesAsNumpy()

	daily_data = {"date": pd.date_range(
		start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
		end =  pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
		freq = pd.Timedelta(seconds = daily.Interval()),
		inclusive = "left"
	)}

	daily_data["weather_code"] = daily_weather_code
	daily_data["sunrise"] = daily_sunrise
	daily_data["sunset"] = daily_sunset
	daily_data["daylight_duration"] = daily_daylight_duration
	daily_data["temperature_2m_max"] = daily_temperature_2m_max
	daily_data["temperature_2m_min"] = daily_temperature_2m_min
	daily_data["temperature_2m_mean"] = daily_temperature_2m_mean
	daily_data["apparent_temperature_mean"] = daily_apparent_temperature_mean
	daily_data["rain_sum"] = daily_rain_sum
	daily_data["showers_sum"] = daily_showers_sum
	daily_data["snowfall_sum"] = daily_snowfall_sum
	daily_data["precipitation_hours"] = daily_precipitation_hours

	daily_dataframe = pd.DataFrame(data = daily_data)
	return daily_dataframe


def main():
	garmin_api = init_api()
	today_run_garmin_stats = extract_today_run_stats(garmin_api)
	recent_garmin_location_stats = extract_location_stats(garmin_api)

	coords = recent_garmin_location_stats["location_coordinates"]
	print(coords)

	params = {
		"latitude": 54.9027,
		"longitude": 23.9096,
		"start_date": "2025-07-04",
		"end_date": "2025-07-04",
		"daily": ["weather_code", "sunrise", "sunset", "daylight_duration", "temperature_2m_max", "temperature_2m_min",
				  "temperature_2m_mean", "apparent_temperature_mean", "rain_sum", "showers_sum", "snowfall_sum",
				  "precipitation_hours"],
		"hourly": ["apparent_temperature", "rain", "showers", "snowfall", "snow_depth", "wind_speed_10m"],
	}
	responses = openmeteo.weather_api(url, params=params)

	print(get_hourly_data(params, responses))
	print(get_daily_data(params, responses))


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		print("Exiting...")
	except Exception as e:
		print(e)
