"""
Parsing helpers for Open-Meteo API responses.
"""

import numpy as np
from datetime import datetime
from typing import Any, Dict


def extract_hourly_data(response, hour: int | None) -> Dict[str, Any]:
    """
    Extract hourly weather metrics.
    Args:
        response (Any): Open-Meteo API response object
        hour (Optional[int]): Hour to extract, if None returns median
    Returns:
        dict: Hourly weather metrics
    """
    hourly = response.Hourly()

    def get_value(index, cast=float):
        values = hourly.Variables(index).ValuesAsNumpy().astype(cast)
        if hour is not None:
            return values[hour].item()
        return np.median(values).item()

    return {
		"hourly_apparent_temperature": round(get_value(0)),
		"hourly_rain_mm": round(get_value(1), 1),
		"hourly_showers_mm": round(get_value(2), 1),
		"hourly_snowfall_mm": round(get_value(3), 1),
		"hourly_snow_depth_cm": round(get_value(4), 1),
		"hourly_wind_speed_10m_kmh": round(get_value(5), 1),
		"hourly_weather_code": get_value(6, int)
	}


def extract_daily_data(response):
    """
    Extract daily aggregated weather metrics.
    Args:
        response (Any): Open-Meteo API response object
    Returns:
        dict: Daily weather metrics
    """
    daily = response.Daily()

    return {
		"daily_weather_code": int(daily.Variables(0).ValuesAsNumpy()[0]),
		"daily_sunrise": datetime.fromtimestamp(daily.Variables(1).ValuesInt64AsNumpy()[0]).strftime("%H:%M:%S"),
		"daily_sunset": datetime.fromtimestamp(daily.Variables(2).ValuesInt64AsNumpy()[0]).strftime("%H:%M:%S"),
		"daily_daylight_duration": int(daily.Variables(3).ValuesAsNumpy()[0] // 3600),
		"daily_temperature_2m_max": round(daily.Variables(4).ValuesAsNumpy()[0]),
		"daily_temperature_2m_min": round(daily.Variables(5).ValuesAsNumpy()[0]),
		"daily_temperature_2m_mean": round(daily.Variables(6).ValuesAsNumpy()[0]),
		"daily_apparent_temperature_mean": round(daily.Variables(7).ValuesAsNumpy()[0]),
		"daily_rain_sum": round(daily.Variables(8).ValuesAsNumpy()[0], 1),
		"daily_showers_sum": round(daily.Variables(9).ValuesAsNumpy()[0], 1),
		"daily_snowfall_sum": round(daily.Variables(10).ValuesAsNumpy()[0], 1),
		"daily_precipitation_hours": round(daily.Variables(11).ValuesAsNumpy()[0]),
	}