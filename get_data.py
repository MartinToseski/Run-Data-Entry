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
import os
import sys
import requests

from datetime import date
from getpass import getpass
from pathlib import Path
from garth.exc import GarthException, GarthHTTPError

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)

from example import init_api


# Suppress garminconnect library logging to avoid tracebacks in normal operation
logging.getLogger("garminconnect").setLevel(logging.CRITICAL)


def extract_stats(api: Garmin):
    """Display today's activity statistics with proper error handling."""
    today = date.today().isoformat()

    return {
        "date": today,
        "training_status": api.get_training_status(today)["mostRecentTrainingStatus"]["latestTrainingStatusData"]["3601168031"]["trainingStatusFeedbackPhrase"],
        "last_night_HRV": api.get_hrv_data(today)["hrvSummary"]["lastNightAvg"],
        "last_night_sleep_score": api.get_sleep_data(today)["dailySleepDTO"]["sleepScores"]["overall"]["value"],
        "last_night_RHR": api.get_rhr_day(today)["allMetrics"]["metricsMap"]["WELLNESS_RESTING_HEART_RATE"][0]["value"]
    }


def main():
    """Main example demonstrating basic Garmin Connect API usage."""
    # Initialize API with authentication (will only prompt for credentials if needed)
    api = init_api()

    if not api:
        return

    # Display daily statistics
    print(extract_stats(api))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Keyboard Interruption!")
    except Exception:
        print("Something bad happened!")
