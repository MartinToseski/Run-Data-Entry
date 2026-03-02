"""
Calendar data extraction and processing helpers.
"""

from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple
from dateutil import parser
from .constants import DEADLINE_KEYWORDS, GYM_AVAILABLE
from code.garmin.utils import get_weekday_name, resolve_date


def get_gym_availability(target_date: date):
    """
    Return gym availability for target date.
    Defaults to False if weekday not configured.
    """
    return GYM_AVAILABLE.get(get_weekday_name(target_date), False)


def is_deadline(event: Dict[str, Any]) -> bool:
    """
    Determine whether an event represents a deadline.
    """
    summary = event.get("summary", "").lower()
    return any(keyword in summary for keyword in DEADLINE_KEYWORDS)


def get_date_window(target_date: date) -> Tuple[str, str]:
    """
    Return ISO timestamps for the target date's UTC window.
    """
    target_date = resolve_date(target_date)
    start = datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    return start.isoformat(), end.isoformat()


def get_next_three_days_window(target_date: date) -> Tuple[str, str]:
    """
    Return ISO timestamps for the next 3-day UTC window.
    """
    target_date = resolve_date(target_date)
    start = datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc)
    end = start + timedelta(days=3)
    return start.isoformat(), end.isoformat()


def process_daily_events(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate duration and time-of-day activity flags.
    Returns:
        dict with:
            - duration_sum (float)
            - morning_activity (bool)
            - evening_activity (bool)
    """
    duration = 0
    before_10am = False
    after_5pm = False

    for event in events:
        if "dateTime" not in event["start"] or "dateTime" not in event["end"]:
            continue

        start = parser.isoparse(event["start"]["dateTime"])
        end = parser.isoparse(event["end"]["dateTime"])

        duration += (end - start).total_seconds() / 3600.0

        if start.hour < 10:
            before_10am = True
        if start.hour > 17:
            after_5pm = True

    return {
        "duration_sum": round(duration, 1),
        "morning_activity": before_10am,
        "evening_activity": after_5pm
    }