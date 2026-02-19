"""🏃‍♂️ Run Data Entry (Run, Will He?) 🏃‍♂️
=======================================

This code extracts information about the following parameters:
- Date
- Location
- Week Total Km. Ran
- Last 4 Weeks Avg. Km. Ran
- Sleep Score
- Last 4 Weeks Avg. Sleep Score
- HRV
- Last 4 Weeks Avg. HRV
- RHR
- Last 4 Weeks Avg. RHR
- Training Status
- Last Run Intensity
- Days Since Last Run
- Days Since Last Quality Session
- Days Since Last Strength Training
- Trip in the Last 2 Weeks?
- Did I Actually Run Today? + Run Intensity + Time of Run

This data is noted in a .csv file with the goal of using it for later data analysis experimenting / ML projects :)

Initial ideas included:
- predicting whether a run will commence today
- analysing best time of the day for me to run (or what time/day I run mostly commonly)
- explain why I ran/didn't run

!!! Credits: https://github.com/cyberjunky/python-garminconnect/tree/master !!!
The provided example.py was used as a starting point to build upon.
"""

import logging
from csv import excel
from datetime import date, timedelta, datetime
from typing import Any, Dict, List, Optional

import geopandas as gpd
from dateutil.relativedelta import relativedelta, MO
from garminconnect import Garmin
from shapely.geometry import Point

from example import init_api


# Suppress garminconnect library logging to avoid tracebacks in normal operation
logging.getLogger("garminconnect").setLevel(logging.CRITICAL)

# ---------------------------------------------------------------------
# Global Data
# ---------------------------------------------------------------------
try:
    WORLD = gpd.read_file("./data/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp")
except Exception as e:
    print("World shapefile could not be loaded:", e)
    WORLD = None

DAYS_OF_THE_WEEK = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}


# ---------------------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------------------
def get_today_date() -> date:
    return date.today()


def get_last_monday() -> date:
    return get_today_date() - relativedelta(weekday=MO(-1))


def get_monday_four_weeks_ago() -> date:
    return get_last_monday() - timedelta(days=28)


def get_weekday_name(date_curr) -> str:
    return DAYS_OF_THE_WEEK[date_curr.weekday()]


def get_total_run_statistic(run_activities: List[dict], stat: str) -> float:
    return sum([run.get(stat, 0) for run in run_activities])


def keep_only_runs(activity_list: List[dict]) -> List[dict]:
    return [activity for activity in activity_list if "running" in activity["activityType"]["typeKey"].split('_')]


def calculate_weighted_training_effect(run_activities: List[dict], effect: str) -> float:
    total_training_load = get_total_run_statistic(run_activities, "activityTrainingLoad")
    if total_training_load == 0:
        return 0.0
    return sum([run.get(effect, 0)*run.get("activityTrainingLoad", 0) for run in run_activities]) / total_training_load


def coordinates_to_country(coords: List[tuple]) -> List[str]:
    if WORLD is None or not coords:
        return []

    country_list = []
    for lat, lon in coords:
        try:
            point = Point(lon, lat)
            match = WORLD[WORLD.geometry.apply(lambda geom: point.within(geom))]

            if not match.empty:
                country_list.append(match.iloc[0]["ADMIN"])
        except Exception:
            continue

    return country_list


def find_trip(country_list: List[str]) -> bool:
    return len(set(country_list)) > 1


# ---------------------------------------------------------------------
# Extraction Functions
# ---------------------------------------------------------------------
def extract_daily_stats(api: Garmin) -> Dict[str, Any]:
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
        "last_night_HRV": hrv,
        "last_night_sleep_score": sleep_score,
        "last_night_RHR": rhr,
        "total_week_km": total_week_km
    }


def extract_today_run_stats(api: Garmin) -> Dict[str, Any]:
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


def extract_last_four_weeks_stats(api: Garmin) -> Dict[str, Any]:
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


def extract_since_last_activity_stats(api: Garmin) -> Dict[str, Any]:
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


def extract_location_stats(api: Garmin) -> Dict[str, Any]:
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
        "trip_in_the_last_two_weeks": find_trip(countries),
    }


def combine_dictionary_data(api: Garmin) -> Dict[str, Any]:
    return extract_daily_stats(api) | extract_today_run_stats(api) | extract_last_four_weeks_stats(api) | extract_since_last_activity_stats(api) | extract_location_stats(api)


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
def main() -> None:
    # Initialize API with authentication (will only prompt for credentials if needed)
    api = init_api()

    if not api:
        print("Lost api")
        return

    print("- - - Garmin Data - - -")
    data = combine_dictionary_data(api)

    print(data)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Keyboard Interruption!")
    except Exception as e:
        print("Something bad happened!\n", e)
