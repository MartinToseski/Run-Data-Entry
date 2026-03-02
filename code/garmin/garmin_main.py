"""
Entry point for Garmin data extraction.
"""

from .client import init_api
from .extract import combine_garmin_data


def main(target_date):
    # Initialize API with authentication (will only prompt for credentials if needed)
    api = init_api()

    if not api:
        print("Lost Garmin api")
        return

    try:
        return combine_garmin_data(api, target_date)
    except Exception as e:
        print("Garmin -", e)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Garmin - Keyboard Interruption!")
    except Exception as e:
        print("Garmin - Something bad happened!\n", e)
