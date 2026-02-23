"""
Calendar data extraction and processing helpers.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple
from dateutil import parser
from .constants import DEADLINE_KEYWORDS, GYM_AVAILABLE
from code.garmin.utils import get_weekday_name, get_today_date


def get_gym_availability():
    return GYM_AVAILABLE[get_weekday_name(get_today_date())]


def is_deadline(event: Dict[str, Any]) -> bool:
    """
    Determine whether an event represents a deadline.
    """
    summary = event.get("summary", "").lower()
    return any(keyword in summary for keyword in DEADLINE_KEYWORDS)


def get_today_window() -> Tuple[str, str]:
    """
    Return ISO timestamps for today's UTC window.
    """
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return start.isoformat(), end.isoformat()


def get_next_three_days_window() -> Tuple[str, str]:
    """
    Return ISO timestamps for the next 3-day UTC window.
    """
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
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
        if "dateTime" not in event["start"]:
            continue

        start = parser.isoparse(event["start"]["dateTime"])
        end = parser.isoparse(event["end"]["dateTime"])

        duration = round((end - start).total_seconds() / 3600.0, 1)

        if start.hour < 10:
            before_10am = True
        if start.hour > 17:
            after_5pm = True

    return {
        "duration_sum": duration,
        "morning_activity": before_10am,
        "evening_activity": after_5pm
    }