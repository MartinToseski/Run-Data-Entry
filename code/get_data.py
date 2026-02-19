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


""" Extract run-focused daily (morning) statistics 
date -> today's date
training_status -> message explaining the current training status (e.g. MAINTAINING_6)
last_night_HRV -> average HRV recorded during last night's sleep (= heart rate variability)
last_night_sleep_score -> score for recorded sleep (from 1 to 100)
last_night_RHR -> average RHR recorded during last night's sleep (= resting heart rate)
total_week_km -> number of kilometers ran this week (from last Monday to today)
"""
def extract_daily_stats(api: Garmin):
    """Display today's summary statistics."""
    today = get_today_date().isoformat()
    last_monday = get_last_monday().isoformat()

    return {
        "date": today,
        "day_of_the_week": get_weekday_name(get_today_date()),
        "training_status": api.get_training_status(today)["mostRecentTrainingStatus"]["latestTrainingStatusData"]["3601168031"]["trainingStatusFeedbackPhrase"],
        "last_night_HRV": api.get_hrv_data(today)["hrvSummary"]["lastNightAvg"],
        "last_night_sleep_score": api.get_sleep_data(today)["dailySleepDTO"]["sleepScores"]["overall"]["value"],
        "last_night_RHR": api.get_rhr_day(today)["allMetrics"]["metricsMap"]["WELLNESS_RESTING_HEART_RATE"][0]["value"],
        "total_week_km": round(sum([run["distance"] for run in api.get_activities_by_date(last_monday, today)]) / 1000, 1)
    }


""" Extract statistics about today's run 
run_today_boolean -> whether a run commenced today (True/False)
run_today_distance_km -> distance ran today
run_today_duration_min -> duration of today's run rounded to minutes 
run_today_training_load -> calculated training load of run (sum of all training loads from the runs that day)
*run_today_aerobic_effect -> calculated aerobic effect of run 
*run_today_aerobic_effect -> calculated anaerobic effect of run 
* -> weighted by load (sum of effect*training load) / total training load 
"""
def extract_today_run_stats(api: Garmin):
    """Display today's activity statistics."""
    today = get_today_date().isoformat()

    today_activities = api.get_activities_by_date(today)
    today_runs = keep_only_runs(today_activities)

    if len(today_runs) == 0:
        return {
            "run_today_boolean": False,
            "run_today_distance_km": 0,
            "run_today_duration_min": 0,
            "run_today_training_load": 0,
            "run_today_aerobic_effect": 0,
            "run_today_anaerobic_effect": 0,
            "run_today_start_time": "00:00:00"
        }

    return {
        "run_today_boolean": True,
        "run_today_distance_km": round(get_total_run_statistic(today_runs, "distance") / 1000, 2),
        "run_today_start_time": min([run["startTimeLocal"].split(' ')[1] for run in today_runs]),
        "run_today_duration_min": round((get_total_run_statistic(today_runs, "duration")) / 60),
        "run_today_training_load": round(get_total_run_statistic(today_runs, "activityTrainingLoad")),
        "run_today_aerobic_effect": round(calculate_weighted_training_effect(today_runs, "aerobicTrainingEffect"), 1),
        "run_today_anaerobic_effect": round(calculate_weighted_training_effect(today_runs, "anaerobicTrainingEffect"), 1)
    }


""" Extract statistics about last 4 weeks
last_four_weeks_average_km -> average weekly kilometers ran
last_four_weeks_average_sleep_score -> average sleep score
last_four_weeks_average_HRV -> average HRV measured
last_four_weeks_average_RHR -> average RHR measured
* the 4 weeks are always calculated from Monday to Sunday no matter the current day of the week
"""
def extract_last_four_weeks_stats(api: Garmin):
    start_date = get_monday_four_weeks_ago()
    end_date = get_last_monday() - timedelta(days=1)
    last_four_weeks_runs = api.get_activities_by_date(startdate=start_date.isoformat(), enddate=end_date.isoformat())
    last_four_weeks_runs = keep_only_runs(last_four_weeks_runs)

    return {
        "last_four_weeks_average_km": round((sum([run["distance"]/1000 for run in last_four_weeks_runs]) / 4), 1),
        "last_four_weeks_average_sleep_score": round(sum([api.get_sleep_data((start_date+timedelta(days=i)).isoformat())["dailySleepDTO"]["sleepScores"]["overall"]["value"] for i in range(28)]) / 28),
        "last_four_weeks_average_HRV": round(sum([api.get_hrv_data((start_date+timedelta(days=i)).isoformat())["hrvSummary"]["lastNightAvg"] for i in range(28)]) / 28),
        "last_four_weeks_average_RHR": round(sum([api.get_rhr_day((start_date+timedelta(days=i)).isoformat())["allMetrics"]["metricsMap"]["WELLNESS_RESTING_HEART_RATE"][0]["value"] for i in range(28)]) / 28)
    }


''' Extract statistics about time since previous sessions
days_since_last_run -> days since last run recorded - outside, treadmill, indoor, or track run (in the last 4 weeks) 
days_since_last_gym -> days since last strength (gym) training recorded (in the last 4 weeks)
days_since_last_quality_session -> days since last run where anaerobic or aerobic training effect was larger than 3 (in the last 4 weeks) 
last_run_aerobic_effect -> aerobic training effect of last run
last_run_anaerobic_effect -> anaerobic training effect of last run
'''
def extract_since_last_activity_stats(api: Garmin):
    last_monday_four_weeks_ago = get_monday_four_weeks_ago()
    yesterday = get_today_date() - timedelta(days=1)

    last_four_weeks_activities = api.get_activities_by_date(last_monday_four_weeks_ago.isoformat(), yesterday.isoformat(), sortorder="desc")
    last_four_weeks_run = keep_only_runs(last_four_weeks_activities)
    last_run = last_four_weeks_run[0]
    last_run_date = datetime.strptime(last_run["startTimeLocal"].split(' ')[0], "%Y-%m-%d").date()

    last_four_weeks_gym = [activity for activity in last_four_weeks_activities if activity["activityName"] == "Strength"]
    last_gym = last_four_weeks_gym[0]
    last_gym_date = datetime.strptime(last_gym["startTimeLocal"].split(' ')[0], "%Y-%m-%d").date()

    last_quality_session = last_run
    for run in last_four_weeks_run:
        if run["aerobicTrainingEffect"] >= 3 or run["anaerobicTrainingEffect"] >= 3:
            last_quality_session = run
            break
    last_quality_session_date = datetime.strptime(last_quality_session["startTimeLocal"].split(' ')[0], "%Y-%m-%d").date()


    return {
        "days_since_last_run": (get_today_date()-last_run_date).days,
        "days_since_last_gym": (get_today_date()-last_gym_date).days,
        "days_since_last_quality_session": (get_today_date()-last_quality_session_date).days,
        "last_run_aerobic_effect": round(last_run["aerobicTrainingEffect"], 1),
        "last_run_anaerobic_effect": round(last_run["anaerobicTrainingEffect"], 1)
    }


def extract_location_stats(api: Garmin):
    today = get_today_date()
    last_monday = get_last_monday()
    two_weeks_before = last_monday - timedelta(days=14)
    last_four_weeks_activities = api.get_activities_by_date(two_weeks_before.isoformat(), today.isoformat(), sortorder="desc")

    locations_list = []
    for run in last_four_weeks_activities:
        run_details = api.get_activity_details(run["activityId"])
        if "geoPolylineDTO" in run_details.keys() and run_details["geoPolylineDTO"] is not None:
            loc = (run_details["geoPolylineDTO"]["startPoint"]["lat"], run_details["geoPolylineDTO"]["startPoint"]["lon"])
            locations_list.append(loc)

    country_list = coordinates_to_country(locations_list)
    trip_in_the_last_two_weeks = find_trip(country_list)

    return {
        "location": country_list[0],
        "trip_in_the_last_two_weeks": trip_in_the_last_two_weeks,
    }


def combine_dictionary_data(api: Garmin):
    return extract_daily_stats(api) | extract_today_run_stats(api) | extract_last_four_weeks_stats(api) | extract_since_last_activity_stats(api) | extract_location_stats(api)


def main():
    """Main example demonstrating basic Garmin Connect API usage."""
    # Initialize API with authentication (will only prompt for credentials if needed)
    api = init_api()

    if not api:
        print("Lost api")
        return

    print("- - - Garmin Data - - -")
    print(combine_dictionary_data(api))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Keyboard Interruption!")
    except Exception:
        print("Something bad happened!")
