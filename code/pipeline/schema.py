"""
Unified dataset schema definition.

This schema reflects the exact keys returned by:
- Garmin extraction
- Weather extraction
- Calendar extraction

The schema ensures:
- Stable column ordering
- Deterministic CSV structure
- Missing fields filled with None
"""

from typing import Dict, List


FINAL_SCHEMA: List[str] = [

    # =========================
    # Garmin — Core Date
    # =========================
    "date",
    "day_of_the_week",

    # =========================
    # Garmin — Recovery & Status
    # =========================
    "training_status",
    "last_night_HRV",
    "last_night_sleep_score",
    "last_night_RHR",

    # =========================
    # Garmin — Weekly Load
    # =========================
    "total_week_km",

    # =========================
    # Garmin — Today Run
    # =========================
    "run_today_boolean",
    "run_today_distance_km",
    "run_today_duration_min",
    "run_today_training_load",
    "run_today_aerobic_effect",
    "run_today_anaerobic_effect",
    "run_today_start_time",

    # =========================
    # Garmin — 4 Week Averages
    # =========================
    "last_four_weeks_average_km",
    "last_four_weeks_average_sleep_score",
    "last_four_weeks_average_HRV",
    "last_four_weeks_average_RHR",

    # =========================
    # Garmin — Recency Metrics
    # =========================
    "days_since_last_run",
    "days_since_last_gym",
    "days_since_last_quality_session",
    "last_run_aerobic_effect",
    "last_run_anaerobic_effect",

    # =========================
    # Garmin — Location
    # =========================
    "location",
    "location_coordinates",
    "trip_in_the_last_two_weeks",

    # =========================
    # Weather — Hourly
    # =========================
    "hourly_apparent_temperature",
    "hourly_rain_mm",
    "hourly_showers_mm",
    "hourly_snowfall_mm",
    "hourly_snow_depth_cm",
    "hourly_wind_speed_10m_kmh",
    "hourly_weather_code",

    # =========================
    # Weather — Daily
    # =========================
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
    "daily_precipitation_hours",

    # =========================
    # Calendar
    # =========================
    "class_hours",
    "work_hours",
    "before_10am",
    "after_5pm",
    "upcoming_deadline_next_three_days",
    "gym_available",
]


def enforce_schema(data: Dict) -> Dict:
    """
    Ensure returned dictionary matches FINAL_SCHEMA exactly.

    - Missing keys → None
    - Extra keys → removed
    - Preserves column ordering
    """
    return {key: data.get(key, None) for key in FINAL_SCHEMA}