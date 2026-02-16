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
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta, MO
from garminconnect import Garmin
from example import init_api

# Suppress garminconnect library logging to avoid tracebacks in normal operation
logging.getLogger("garminconnect").setLevel(logging.CRITICAL)

days_of_the_week = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}

""" Helper function to get today's date """
def get_today_date():
    today_date = date.today()
    return today_date


""" Helper function to get last Monday's date before today's date """
def get_last_monday():
    last_monday_date = get_today_date() - relativedelta(weekday=MO(-1))
    return last_monday_date


""" Helper function to get the name of the weekday from the date provided """
def get_weekday_name(date_curr):
    return days_of_the_week[date_curr.weekday()]


""" Helper function to get a sum of some statistic in a list of runs """
def get_total_run_statistic(run_activities, stat):
    today = get_today_date().isoformat()
    return sum([run[stat] for run in run_activities])


""" Helper function to get the date of Monday four weeks ago  """
def get_monday_four_weeks_ago():
    last_monday = get_last_monday()
    monday_four_weeks_ago = last_monday - timedelta(days=28)
    return monday_four_weeks_ago


""" Helper function to retain all run type activities from a list of activities """
def keep_only_runs(activity_list):
    return [activity for activity in activity_list if activity["activityType"]["parentTypeId"] == 1]


""" Helper function to calculate the weighted training effect for a list of runs
effect -> aerobicTrainingEffect / anaerobicTrainingEffect
"""
def calculate_weighted_training_effect(run_activities, effect):
    today = get_today_date().isoformat()
    total_training_load = get_total_run_statistic(run_activities, "activityTrainingLoad")
    return sum([run[effect]*run["activityTrainingLoad"] for run in run_activities]) / total_training_load



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
            "tun_today_start_time": "00:00:00"
        }

    return {
        "run_today_boolean": True,
        "run_today_distance_km": get_total_run_statistic(today_runs, "distance") / 1000,
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
    last_four_weeks_runs = api.get_activities_by_date(startdate=start_date.isoformat(), enddate=end_date.isoformat(), sortorder="asc")
    last_four_weeks_runs = keep_only_runs(last_four_weeks_runs)

    return {
        "last_four_weeks_average_km": round((sum([run["distance"]/1000 for run in last_four_weeks_runs]) / 4), 1),
        "last_four_weeks_average_sleep_score": round(sum([api.get_sleep_data((start_date+timedelta(days=i)).isoformat())["dailySleepDTO"]["sleepScores"]["overall"]["value"] for i in range(28)]) / 28),
        "last_four_weeks_average_HRV": round(sum([api.get_hrv_data((start_date+timedelta(days=i)).isoformat())["hrvSummary"]["lastNightAvg"] for i in range(28)]) / 28),
        "last_four_weeks_average_RHR": round(sum([api.get_rhr_day((start_date+timedelta(days=i)).isoformat())["allMetrics"]["metricsMap"]["WELLNESS_RESTING_HEART_RATE"][0]["value"] for i in range(28)]) / 28)
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
    print(extract_today_run_stats(api), "\n")

    # Display last 4 weeks average statistics
    print("Last 4 Weeks Stats:")
    print(extract_last_four_weeks_stats(api))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Keyboard Interruption!")
    except Exception:
        print("Something bad happened!")
