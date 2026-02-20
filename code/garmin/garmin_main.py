"""
Entry point for Garmin data extraction.
"""

from .example import init_api
from .extract import combine_dictionary_data


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
