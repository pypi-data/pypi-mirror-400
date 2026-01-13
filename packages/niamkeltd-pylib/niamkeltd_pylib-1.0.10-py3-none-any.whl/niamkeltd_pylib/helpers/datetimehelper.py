from typing import Optional
import pytz, calendar, logging
from datetime import datetime, timedelta, UTC
from niamkeltd_pylib.models.weekday import Weekday

def week_starting(week_number: int, year: int) -> datetime:
    # January 4th is always in week 1
    jan_4 = datetime(year, 1, 4)
    # Calculate the start of the year i.e. the Monday of week 1
    start_of_iso_year = jan_4 - timedelta(days=jan_4.isoweekday() - 1)
    # Add weeks to get to the target week
    week_start_date = start_of_iso_year + timedelta(weeks=week_number - 1)
    return week_start_date

def start_of_month(today : datetime) -> datetime:
    return datetime(today.year, today.month, 1)

def end_of_month(today : datetime) -> datetime:
    return datetime(today.year, today.month, calendar.monthrange(today.year, today.month)[1])

def add_days(target_date : datetime, days : int) -> datetime:
    return target_date + timedelta(days=days)

def previous_weekday(weekday : Weekday, now : datetime) -> datetime:
    offset = (now.weekday() - weekday.id) % 7
    previous_weekday = add_days(now, -offset)
    logging.info(f"Previous weekday: {previous_weekday}")
    return previous_weekday

def next_weekday(weekday : Weekday, now : datetime) -> datetime:
    today_weekday = now.weekday()
    offset = ((7 + weekday.id) - today_weekday) % 7 if today_weekday != 0 else 7
    next_weekday = add_days(now, offset)
    logging.info(f"Next Weekday: {next_weekday}")
    return next_weekday

def utc_now() -> datetime:
    return datetime.now(UTC)

def now() -> datetime:
    return datetime.now(pytz.timezone('Europe/London'))

def calculate_age(dob: datetime, now: Optional[datetime] = None) -> int:
    now = datetime.now(UTC) if not now else now
    age = now.year - dob.year - 1 if (now.month, now.day) < (dob.month, dob.day) else now.year - dob.year
    return age