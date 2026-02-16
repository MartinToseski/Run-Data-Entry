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
from datetime import date
from dateutil.relativedelta import relativedelta, MO
from garminconnect import Garmin
from example import init_api

# Suppress garminconnect library logging to avoid tracebacks in normal operation
logging.getLogger("garminconnect").setLevel(logging.CRITICAL)


""" Helper function to get today's date """
def get_today_date():
    today_date = date.today()
    return today_date


""" Helper function to get last Monday's date before today's date """
def get_last_monday():
    last_monday_date = get_today_date() - relativedelta(weekday=MO(-1))
    return last_monday_date


""" Helper function to retain all run type activities from a list of activities """
def keep_only_runs(activity_list):
    return [activity for activity in activity_list if activity["activityType"]["parentTypeId"] == 1]


""" Helper function to get a sum of some statistic in a list of runs """
def get_total_run_statistic(api: Garmin, run_activities, stat):
    today = get_today_date().isoformat()
    return sum([api.get_activities_by_date(today)[i][stat] for i in range(0, len(run_activities))])


""" Helper function to calculate the weighted training effect for a list of runs
effect -> aerobicTrainingEffect / anaerobicTrainingEffect
"""
def calculate_weighted_training_effect(api: Garmin, run_activities, effect):
    today = get_today_date().isoformat()
    total_training_load = get_total_run_statistic(api, run_activities, "activityTrainingLoad")
    return sum([api.get_activities_by_date(today)[i][effect]*api.get_activities_by_date(today)[i]["activityTrainingLoad"] for i in range(0, len(run_activities))]) / total_training_load



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
        "training_status": api.get_training_status(today)["mostRecentTrainingStatus"]["latestTrainingStatusData"]["3601168031"]["trainingStatusFeedbackPhrase"],
        "last_night_HRV": api.get_hrv_data(today)["hrvSummary"]["lastNightAvg"],
        "last_night_sleep_score": api.get_sleep_data(today)["dailySleepDTO"]["sleepScores"]["overall"]["value"],
        "last_night_RHR": api.get_rhr_day(today)["allMetrics"]["metricsMap"]["WELLNESS_RESTING_HEART_RATE"][0]["value"],
        "total_week_km": api.get_activities_by_date(last_monday, today)[0]["distance"] / 1000
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
def extract_today_run(api: Garmin):
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
            "run_today_anaerobic_effect": 0
        }

    return {
        "run_today_boolean": True,
        "run_today_distance_km": get_total_run_statistic(api, today_runs, "distance") / 1000,
        "run_today_duration_min": round((get_total_run_statistic(api, today_runs, "duration")) / 60),
        "run_today_training_load": round(get_total_run_statistic(api, today_runs, "activityTrainingLoad")),
        "run_today_aerobic_effect": round(calculate_weighted_training_effect(api, today_runs, "aerobicTrainingEffect"), 1),
        "run_today_anaerobic_effect": round(calculate_weighted_training_effect(api, today_runs, "anaerobicTrainingEffect"), 1),
    }


def main():
    """Main example demonstrating basic Garmin Connect API usage."""
    # Initialize API with authentication (will only prompt for credentials if needed)
    api = init_api()

    if not api:
        return

    # Display daily statistics
    print("Daily Stats:")
    print(extract_daily_stats(api), "\n")

    # Display today's run statistics
    print("Today's Run Stats:")
    print(extract_today_run(api))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Keyboard Interruption!")
    except Exception:
        print("Something bad happened!")
