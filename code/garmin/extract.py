"""
Extraction of daily health metrics and weekly run totals,
today's run-specific metrics,
rolling four-weeks averages,
days since different previous activities,
and location information
"""

from datetime import timedelta, datetime
from typing import Any, Dict
from garminconnect import Garmin
from .utils import get_today_date, get_last_monday, get_monday_four_weeks_ago, get_weekday_name, get_total_run_statistic, keep_only_runs, calculate_weighted_training_effect
from .geo import coordinates_to_country, find_trip


# ---------------------------------------------------------------------
# Daily Metrics
# ---------------------------------------------------------------------
def extract_daily_stats(api: Garmin) -> Dict[str, Any]:
    """
    Extract today's recovery and weekly running metrics.
    Includes:
        - Training status
        - HRV
        - Sleep score
        - Resting heart rate
        - Total kilometers run this week
    Returns:
        Dictionary containing daily health and weekly mileage metrics.
    All fields default to None or 0 if API calls fail.
    """
    today = get_today_date().isoformat()
    last_monday = get_last_monday().isoformat()

    try:
        training_status_data = api.get_training_status(today)
        training_status = training_status_data.get("mostRecentTrainingStatus", {}).get("latestTrainingStatusData", {}).get("3601168031", {}).get("trainingStatusFeedbackPhrase")
    except Exception:
        training_status = None

    try:
        hrv = api.get_hrv_data(today).get("hrvSummary", {}).get("lastNightAvg")
    except Exception:
        hrv = None

    try:
        sleep_score = api.get_sleep_data(today).get("dailySleepDTO", {}).get("sleepScores", {}).get("overall", {}).get("value")
    except Exception:
        sleep_score = None

    try:
        rhr = api.get_rhr_day(today).get("allMetrics", {}).get("metricsMap", {}).get("WELLNESS_RESTING_HEART_RATE", [{}])[0].get("value")
    except Exception:
        rhr = None

    try:
        week_activities = api.get_activities_by_date(last_monday, today)
        week_runs = keep_only_runs(week_activities)
        total_week_km = round(sum(run.get("distance", 0) for run in week_runs) / 1000, 1)
    except Exception:
        total_week_km = 0

    return {
        "date": today,
        "day_of_the_week": get_weekday_name(get_today_date()),
        "training_status": training_status,
        "last_night_HRV": int(round(hrv)),
        "last_night_sleep_score": int(round(sleep_score)),
        "last_night_RHR": int(round(rhr)),
        "total_week_km": total_week_km
    }


# ---------------------------------------------------------------------
# Today's Run
# ---------------------------------------------------------------------
def extract_today_run_stats(api: Garmin) -> Dict[str, Any]:
    """
    Determine whether a run occurred today and extract its metrics.
    Includes:
        - Distance
        - Duration
        - Training load
        - Aerobic and anaerobic effect
        - Start time
    Returns:
        Dictionary with run metrics. If no run occurred,
        values are set to defaults and run_today_boolean is False.
    """
    today = get_today_date().isoformat()

    try:
        today_activities = api.get_activities_by_date(today)
    except Exception:
        today_activities = None
    today_runs = keep_only_runs(today_activities)

    if len(today_runs) == 0:
        return {
            "run_today_boolean": False,
            "run_today_distance_km": 0.0,
            "run_today_duration_min": 0,
            "run_today_training_load": 0,
            "run_today_aerobic_effect": 0.0,
            "run_today_anaerobic_effect": 0.0,
            "run_today_start_time": None
        }

    return {
        "run_today_boolean": True,
        "run_today_distance_km": round(get_total_run_statistic(today_runs, "distance") / 1000, 2),
        "run_today_start_time": min(run.get("startTimeLocal", "").split(' ')[1] for run in today_runs if "startTimeLocal" in run),
        "run_today_duration_min": round(get_total_run_statistic(today_runs, "duration") / 60),
        "run_today_training_load": round(get_total_run_statistic(today_runs, "activityTrainingLoad")),
        "run_today_aerobic_effect": round(calculate_weighted_training_effect(today_runs, "aerobicTrainingEffect"), 1),
        "run_today_anaerobic_effect": round(calculate_weighted_training_effect(today_runs, "anaerobicTrainingEffect"), 1)
    }


# ---------------------------------------------------------------------
# Four Week Averages
# ---------------------------------------------------------------------
def extract_last_four_weeks_stats(api: Garmin) -> Dict[str, Any]:
    """
    Compute rolling four-week averages.
    Includes:
        - Average weekly kilometers
        - Average sleep score
        - Average HRV
        - Average resting heart rate
    The time window spans the four full weeks preceding the current week.
    """
    start_date = get_monday_four_weeks_ago()
    end_date = get_last_monday() - timedelta(days=1)

    try:
        activities = api.get_activities_by_date(startdate=start_date.isoformat(), enddate=end_date.isoformat())
        runs = keep_only_runs(activities)
        avg_km = round(sum(run.get("distance", 0) / 1000 for run in runs) / 4, 1)
    except Exception:
        avg_km = 0

    return {
        "last_four_weeks_average_km": avg_km,
        "last_four_weeks_average_sleep_score": round(sum(api.get_sleep_data((start_date+timedelta(days=i)).isoformat()).get("dailySleepDTO", {}).get("sleepScores", {}).get("overall", {}).get("value") for i in range(28)) / 28),
        "last_four_weeks_average_HRV": round(sum(api.get_hrv_data((start_date+timedelta(days=i)).isoformat()).get("hrvSummary", {}).get("lastNightAvg", {}) for i in range(28)) / 28),
        "last_four_weeks_average_RHR": round(sum(api.get_rhr_day((start_date+timedelta(days=i)).isoformat()).get("allMetrics", {}).get("metricsMap", {}).get("WELLNESS_RESTING_HEART_RATE", [{}])[0].get("value") for i in range(28)) / 28)
    }


# ---------------------------------------------------------------------
# Recency Metrics
# ---------------------------------------------------------------------
def extract_since_last_activity_stats(api: Garmin) -> Dict[str, Any]:
    """
    Compute recency metrics for key activity types.
    Includes:
        - Days since last run
        - Days since last strength session
        - Days since last quality session
        - Aerobic/anaerobic effect of most recent run
    Returns:
        Dictionary with recency and intensity indicators.
    """
    last_monday_four_weeks_ago = get_monday_four_weeks_ago()
    yesterday = get_today_date() - timedelta(days=1)

    try:
        activities = api.get_activities_by_date(last_monday_four_weeks_ago.isoformat(), yesterday.isoformat(), sortorder="desc")
    except Exception:
        activities = []

    runs = keep_only_runs(activities)

    if runs:
        last_run = runs[0]
        last_run_date = datetime.strptime(last_run.get("startTimeLocal", "").split(' ')[0], "%Y-%m-%d").date()
        days_since_last_run = (get_today_date() - last_run_date).days
        last_run_aerobic = round(last_run.get("aerobicTrainingEffect", 0), 1)
        last_run_anaerobic = round(last_run.get("anaerobicTrainingEffect", 0), 1)
    else:
        days_since_last_run = None
        last_run_aerobic = None
        last_run_anaerobic = None

    gym_sessions = [activity for activity in activities if activity.get("activityName", "") == "Strength"]
    if gym_sessions:
        last_gym = gym_sessions[0]
        last_gym_date = datetime.strptime(last_gym.get("startTimeLocal", "").split(' ')[0], "%Y-%m-%d").date()
        days_since_last_gym = (get_today_date() - last_gym_date).days
    else:
        days_since_last_gym = None

    quality_session = [activity for activity in activities if activity not in gym_sessions and activity.get("aerobicTrainingEffect", 0) >= 3 or activity.get("anaerobicTrainingEffect", 0) >= 3]
    if quality_session:
        last_quality_session = quality_session[0]
        last_quality_session_date = datetime.strptime(last_quality_session.get("startTimeLocal", "").split(' ')[0], "%Y-%m-%d").date()
        days_since_last_quality_session = (get_today_date() - last_quality_session_date).days
    else:
        days_since_last_quality_session = None


    return {
        "days_since_last_run": days_since_last_run,
        "days_since_last_gym": days_since_last_gym,
        "days_since_last_quality_session": days_since_last_quality_session,
        "last_run_aerobic_effect": last_run_aerobic,
        "last_run_anaerobic_effect": last_run_anaerobic
    }


# ---------------------------------------------------------------------
# Location
# ---------------------------------------------------------------------
def extract_location_stats(api: Garmin) -> Dict[str, Any]:
    """
    Infer location and travel behavior from recent run coordinates.
    Includes:
        - Most recent detected country
        - Boolean indicating travel within last two weeks
    Uses start coordinates of runs for country detection.
    """
    today = get_today_date()
    two_weeks_before = get_last_monday() - timedelta(days=14)

    try:
        activities = api.get_activities_by_date(two_weeks_before.isoformat(), today.isoformat(), sortorder="desc")
    except Exception:
        activities = []

    runs = keep_only_runs(activities)
    locations = []

    for run in runs:
        try:
            details = api.get_activity_details(run["activityId"])
            geo = details.get("geoPolylineDTO")
            if geo:
                lat = geo["startPoint"].get("lat")
                lon = geo["startPoint"].get("lon")
                locations.append((lat, lon))
        except Exception:
            continue

    countries = coordinates_to_country(locations)

    return {
        "location": countries[0],
        "location_coordinates": locations[0],
        "trip_in_the_last_two_weeks": find_trip(countries)
    }


def combine_garmin_data(api: Garmin) -> Dict[str, Any]:
    """
    Aggregate all extraction modules into a single unified dictionary.
    Serves as the primary interface for downstream persistence
    (e.g., CSV storage or database insertion).
    """ 
    return extract_daily_stats(api) | extract_today_run_stats(api) | extract_last_four_weeks_stats(api) | extract_since_last_activity_stats(api) | extract_location_stats(api)