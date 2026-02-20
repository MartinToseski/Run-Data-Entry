"""
General utility helpers used across extraction modules.
"""

from datetime import date, timedelta
from typing import List
from dateutil.relativedelta import relativedelta, MO
from .config import DAYS_OF_THE_WEEK


def get_today_date() -> date:
    """
    Return the current calendar date.
    Used as the single source of truth for all date-based calculations.
    """
    return date.today()


def get_last_monday() -> date:
    """
    Return the date of the most recent Monday.
    Used to define weekly aggregation windows.
    """
    return get_today_date() - relativedelta(weekday=MO(-1))


def get_monday_four_weeks_ago() -> date:
    """
    Return the Monday four weeks prior to the most recent Monday.
    Defines the rolling 4-week analysis window.
    """
    return get_last_monday() - timedelta(days=28)


def get_weekday_name(date_curr) -> str:
    """
    Return the weekday name (e.g., 'Monday') for a given date.
    """
    return DAYS_OF_THE_WEEK[date_curr.weekday()]


def get_total_run_statistic(run_activities: List[dict], stat: str) -> float:
    """
    Sum a numeric statistic across a list of run activities.
    Parameters:
        run_activities: List of Garmin activity dictionaries.
        stat: Key of the numeric metric to aggregate.
    Returns:
        Total value of the specified metric.
    """
    return sum([run.get(stat, 0) for run in run_activities])


def keep_only_runs(activity_list: List[dict]) -> List[dict]:
    """
    Filter activity list to include only running activities.
    Assumes Garmin activityType.typeKey contains 'running'.
    """
    return [activity for activity in activity_list if "running" in activity["activityType"]["typeKey"].split('_')]


def calculate_weighted_training_effect(run_activities: List[dict], effect: str) -> float:
    """
    Compute training-load weighted aerobic or anaerobic effect.
    Returns 0.0 if total training load is zero.
    """
    total_training_load = get_total_run_statistic(run_activities, "activityTrainingLoad")
    if total_training_load == 0:
        return 0.0
    return sum([run.get(effect, 0)*run.get("activityTrainingLoad", 0) for run in run_activities]) / total_training_load