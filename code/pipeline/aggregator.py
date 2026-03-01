"""
Data aggregation layer.

Combines:
- Garmin
- Weather
- Calendar

Returns a single flat dictionary ready for storage.
"""

from code.garmin.garmin_main import main as garmin_main
from code.weather.weather_main import main as weather_main
from code.calendar.calendar_main import main as calendar_main
from .schema import enforce_schema


def aggregate_all():
    garmin_data = garmin_main()
    print(garmin_data)
    weather_data = weather_main()
    print(weather_data)
    calendar_data = calendar_main()
    print(calendar_data)

    combined = garmin_data | weather_data | calendar_data
    return enforce_schema(combined)