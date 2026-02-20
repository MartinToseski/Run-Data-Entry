"""
Open-Meteo client configuration with caching and retry behavior.
"""

import requests_cache
import openmeteo_requests
from retry_requests import retry


def build_weather_client():
    """
    Build and return an Open-Meteo client with caching and retry.
    Returns:
        Client: Configured Open-Meteo client
    """
    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    return openmeteo_requests.Client(session=retry_session)