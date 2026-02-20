import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry
from code.garmin.utils import get_today_date


# Set up the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)


# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
today = get_today_date()
print(today)
params = {
	"latitude": 54.9027,
	"longitude": 23.9096,
	"start_date": "2025-07-04",
	"end_date": "2025-07-04",
	"hourly": "temperature_2m",
}


def main():
    return "Hello Main"


if __name__ == "__main__":
    print(main())
