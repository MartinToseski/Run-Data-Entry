"""
Calendar data extraction entry point.

Fetches:
- Class hours today
- Work hours today
- Morning / evening activity flags
- Upcoming deadlines within 3 days
"""

from typing import Any, Dict, List
from googleapiclient.errors import HttpError
from .client import build_calendar_service
from .constants import CLASS_CALENDAR_NAME, WORK_CALENDAR_NAME
from .parsing import get_today_window, get_next_three_days_window, process_daily_events, is_deadline, get_gym_availability


def get_calendar_id(service, calendar_name) -> str | None:
    """
    Retrieve calendar ID by calendar name.
    """
    calendars = service.calendarList().list().execute()
    for calendar in calendars["items"]:
        if calendar_name == calendar["summary"]:
            return calendar["id"]
    return None


def get_events(service, calendar_id, start, end) -> List[Dict[str, Any]]:
    """
    Fetch events within a time window.
    """
    events = (
        service.events()
        .list(calendarId=calendar_id, timeMin=start, timeMax=end, singleEvents=True, orderBy="startTime")
        .execute()
        .get("items", [])
    )
    return events


def extract_calendar_stats() -> Dict[str, Any]:
    """
    Extract structured calendar metrics.
    """
    service = build_calendar_service()

    class_calendar_id = get_calendar_id(service, CLASS_CALENDAR_NAME)
    work_calendar_id = get_calendar_id(service, WORK_CALENDAR_NAME)

    if not class_calendar_id or not work_calendar_id:
        raise ValueError("Required calendars not found.")

    start, end = get_today_window()
    classes_today = get_events(service, class_calendar_id, start, end)
    work_today = get_events(service, work_calendar_id, start, end)

    classes_stats = process_daily_events(classes_today)
    work_stats = process_daily_events(work_today)

    deadlines_start, deadlines_end = get_next_three_days_window()
    events_next_three_days = get_events(service, work_calendar_id, deadlines_start, deadlines_end)
    upcoming_deadlines = [event for event in events_next_three_days if is_deadline(event)]

    return {
        "class_hours": classes_stats["duration_sum"],
        "work_hours": work_stats["duration_sum"],
        "before_10am": classes_stats["morning_activity"] or work_stats["morning_activity"],
        "after_5pm": classes_stats["evening_activity"] or work_stats["evening_activity"],
        "upcoming_deadline_next_three_days": len(upcoming_deadlines) > 0,
        "gym_available": get_gym_availability()
    }


def main():
    """
    Entry point for standalone execution.
    """
    try:
        return extract_calendar_stats()
    except HttpError as e:
        print(e)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting Calendar...")
    except Exception as e:
        print("Calendar -", e)