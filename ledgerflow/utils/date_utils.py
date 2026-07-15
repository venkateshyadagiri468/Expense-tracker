from datetime import date, datetime, timedelta
from typing import Tuple, Union


def parse_date(date_val: Union[str, date]) -> date:
    """Parses a date from string or passes through if already a date."""
    if isinstance(date_val, date) and not isinstance(date_val, datetime):
        return date_val
    if isinstance(date_val, datetime):
        return date_val.date()
    try:
        return datetime.strptime(str(date_val).strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Invalid date format. Expected YYYY-MM-DD.")


def get_today_range() -> Tuple[date, date]:
    """Returns starting and ending date for today."""
    today = date.today()
    return today, today


def get_current_week_range() -> Tuple[date, date]:
    """Returns starting (Monday) and ending (Sunday) date for the current week."""
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week


def get_current_month_range() -> Tuple[date, date]:
    """Returns starting and ending date for the current month."""
    today = date.today()
    start_of_month = date(today.year, today.month, 1)
    if today.month == 12:
        end_of_month = date(today.year, 12, 31)
    else:
        end_of_month = date(today.year, today.month + 1, 1) - timedelta(days=1)
    return start_of_month, end_of_month


def get_current_year_range() -> Tuple[date, date]:
    """Returns starting and ending date for the current year."""
    today = date.today()
    start_of_year = date(today.year, 1, 1)
    end_of_year = date(today.year, 12, 31)
    return start_of_year, end_of_year


def get_month_range(year: int, month: int) -> Tuple[date, date]:
    """Returns starting and ending date for a specific month and year."""
    start_of_month = date(year, month, 1)
    if month == 12:
        end_of_month = date(year, 12, 31)
    else:
        end_of_month = date(year, month + 1, 1) - timedelta(days=1)
    return start_of_month, end_of_month
