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


# Suppress garminconnect library logging to avoid tracebacks in normal operation
logging.getLogger("garminconnect").setLevel(logging.CRITICAL)


def safe_api_call(api_method, *args, **kwargs):
    """Safe API call wrapper with comprehensive error handling.

    This demonstrates the error handling patterns used throughout the library.
    Returns (success: bool, result: Any, error_message: str)
    """
    try:
        result = api_method(*args, **kwargs)
        return True, result, None

    except GarthHTTPError as e:
        # Handle specific HTTP errors gracefully
        error_str = str(e)
        status_code = getattr(getattr(e, "response", None), "status_code", None)

        if status_code == 400 or "400" in error_str:
            return (
                False,
                None,
                "Endpoint not available (400 Bad Request) - Feature may not be enabled for your account",
            )
        if status_code == 401 or "401" in error_str:
            return (
                False,
                None,
                "Authentication required (401 Unauthorized) - Please re-authenticate",
            )
        if status_code == 403 or "403" in error_str:
            return (
                False,
                None,
                "Access denied (403 Forbidden) - Account may not have permission",
            )
        if status_code == 404 or "404" in error_str:
            return (
                False,
                None,
                "Endpoint not found (404) - Feature may have been moved or removed",
            )
        if status_code == 429 or "429" in error_str:
            return (
                False,
                None,
                "Rate limit exceeded (429) - Please wait before making more requests",
            )
        if status_code == 500 or "500" in error_str:
            return (
                False,
                None,
                "Server error (500) - Garmin's servers are experiencing issues",
            )
        if status_code == 503 or "503" in error_str:
            return (
                False,
                None,
                "Service unavailable (503) - Garmin's servers are temporarily unavailable",
            )
        return False, None, f"HTTP error: {e}"

    except FileNotFoundError:
        return (
            False,
            None,
            "No valid tokens found. Please login with your email/password to create new tokens.",
        )

    except GarminConnectAuthenticationError as e:
        return False, None, f"Authentication issue: {e}"

    except GarminConnectConnectionError as e:
        return False, None, f"Connection issue: {e}"

    except GarminConnectTooManyRequestsError as e:
        return False, None, f"Rate limit exceeded: {e}"

    except Exception as e:
        return False, None, f"Unexpected error: {e}"


def get_credentials():
    """Get email and password from environment or user input."""
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    if not email:
        email = input("Login email: ")
    if not password:
        password = getpass("Enter password: ")

    return email, password


def init_api() -> Garmin | None:
    """Initialize Garmin API with authentication and token management."""
    # Configure token storage
    tokenstore = os.getenv("GARMINTOKENS", "~/.garminconnect")
    tokenstore_path = Path(tokenstore).expanduser()

    # Check if token files exist
    if tokenstore_path.exists():
        token_files = list(tokenstore_path.glob("*.json"))
        if token_files:
            pass
        else:
            pass
    else:
        pass

    # First try to log in with stored tokens
    try:
        garmin = Garmin()
        garmin.login(str(tokenstore_path))
        return garmin

    except (
        FileNotFoundError,
        GarthHTTPError,
        GarminConnectAuthenticationError,
        GarminConnectConnectionError,
    ):
        pass

    # Loop for credential entry with retry on auth failure
    while True:
        try:
            # Get credentials
            email, password = get_credentials()

            garmin = Garmin(
                email=email, password=password, is_cn=False, return_on_mfa=True
            )
            result1, result2 = garmin.login()

            if result1 == "needs_mfa":
                mfa_code = input("Please enter your MFA code: ")

                try:
                    garmin.resume_login(result2, mfa_code)

                except GarthHTTPError as garth_error:
                    # Handle specific HTTP errors from MFA
                    error_str = str(garth_error)
                    if "429" in error_str and "Too Many Requests" in error_str:
                        sys.exit(1)
                    elif "401" in error_str or "403" in error_str:
                        continue
                    else:
                        # Other HTTP errors - don't retry
                        sys.exit(1)

                except GarthException:
                    continue

            # Save tokens for future use
            garmin.garth.dump(str(tokenstore_path))
            return garmin

        except GarminConnectAuthenticationError:
            # Continue the loop to retry
            continue

        except (
            FileNotFoundError,
            GarthHTTPError,
            GarminConnectConnectionError,
            requests.exceptions.HTTPError,
        ):
            return None

        except KeyboardInterrupt:
            return None


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
