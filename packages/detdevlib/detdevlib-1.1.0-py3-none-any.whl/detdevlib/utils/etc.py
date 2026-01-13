from datetime import date, datetime, timedelta, tzinfo
from typing import Callable
from zoneinfo import ZoneInfo

import pandas as pd

AMS_TZ = ZoneInfo("Europe/Amsterdam")
UTC_TZ = ZoneInfo("UTC")


def safe_int(x: str) -> int | None:
    """Converts a string to int if possible, otherwise returns None."""
    try:
        return int(x)
    except ValueError:
        return None


def clean_dict(d: dict) -> dict:
    """Removes all None values from a dictionary."""
    return {k: v for k, v in d.items() if v is not None}


def is_dst_adj_day(date_obj: date) -> bool:
    """Checks if a given date is a day when Daylight Saving Time (DST) adjustment occurs.

    Assumes Amsterdam locality.
    """
    next_date_obj = date_obj + timedelta(days=1)

    day_start = datetime(date_obj.year, date_obj.month, date_obj.day, tzinfo=AMS_TZ)
    next_day_start = datetime(
        next_date_obj.year, next_date_obj.month, next_date_obj.day, tzinfo=AMS_TZ
    )

    duration_of_day = next_day_start - day_start
    return duration_of_day != timedelta(hours=24)


def safe_reset_index(df: pd.DataFrame, inplace: bool = False) -> pd.DataFrame:
    """Reset index safely by renaming index columns if they conflict with existing columns."""
    # Get current index names
    new_names = list(df.index.names)
    existing_cols = set(df.columns)

    for i, name in enumerate(new_names):
        # Handle unnamed indexes (None)
        if name is None:
            # Emulate pandas default naming: 'index' for single, 'level_x' for multi
            base_name = "index" if len(new_names) == 1 else f"level_{i}"
        else:
            base_name = name

        # Check for collision and rename if necessary
        candidate = base_name
        counter = 1

        # Keep appending suffix until the name is unique among columns
        # AND unique among other new index names we are generating
        while candidate in existing_cols:
            candidate = f"{base_name}_{counter}"
            counter += 1

        new_names[i] = candidate
        # Add to existing_cols so subsequent levels don't collide with this one
        existing_cols.add(candidate)

    # Apply new safe names and reset
    if inplace:
        df.index.names = new_names
        df.reset_index(inplace=True, drop=False)
        return df
    else:
        df = df.copy()
        df.index.names = new_names
        return df.reset_index(inplace=False, drop=False)


def standardize_to_utc(series: pd.Series) -> pd.Series:
    """Converts a Series (object or datetime) to UTC datetime.

    Logic:
    1. Converts object/string to datetime.
    2. Naive datetimes are localized to UTC (Assumed UTC).
    3. Aware datetimes are converted to UTC.
    """
    return pd.to_datetime(series, utc=True)


def time_range(
    start_dt: datetime, end_dt: datetime, step: Callable[[datetime], datetime]
):
    """Generates a sequence of datetimes from start_dt up to (but not including) end_dt."""
    current_dt = start_dt
    while current_dt < end_dt:
        yield current_dt
        next_dt = step(current_dt)
        if next_dt <= current_dt:
            raise ValueError("Step function must be strictly increasing in time.")
        current_dt = next_dt


def time_blocks(
    start_dt: datetime, end_dt: datetime, step: Callable[[datetime], datetime]
):
    """Generates contiguous time intervals (blocks) covering the duration from start_dt to end_dt."""
    gen = time_range(start_dt, end_dt, step)
    prev = next(gen)
    for dt in gen:
        yield prev, dt
        prev = dt
    yield prev, end_dt


def safe_localize(dt_naive: datetime, tz: tzinfo | None) -> datetime:
    """Localizes a naive datetime to a specific time zone.

    Handles ambiguous and non-existent times (DST transitions) deterministically.
    """
    if dt_naive.tzinfo is not None:
        raise ValueError("dt_naive must be naive")
    if tz is None:
        return dt_naive
    dt = dt_naive.replace(tzinfo=tz, fold=0)
    dt_utc = dt.astimezone(UTC_TZ)
    dt_checked = dt_utc.astimezone(tz)
    return dt_checked


def to_timezone(dt: datetime, tz: tzinfo) -> datetime:
    """Converts a datetime to a specific time zone.

    If the datetime is naive, it is localized to the given time zone (using safe_localize).
    If the datetime is aware, it is converted to the given time zone.
    """
    if dt.tzinfo is None:
        return safe_localize(dt, tz)
    return dt.astimezone(tz)


def start_of_second(dt: datetime) -> datetime:
    """Floors to the beginning of the current second (removes microseconds)."""
    tz = dt.tzinfo
    dt_naive = dt.replace(tzinfo=None)
    dt_naive = dt_naive.replace(microsecond=0)
    return safe_localize(dt_naive, tz)


def start_of_minute(dt: datetime) -> datetime:
    """Floors to the beginning of the current minute (:00)."""
    tz = dt.tzinfo
    dt_naive = dt.replace(tzinfo=None)
    dt_naive = dt_naive.replace(second=0, microsecond=0)
    return safe_localize(dt_naive, tz)


def start_of_hour(dt: datetime) -> datetime:
    """Floors to the beginning of the current hour (:00:00)."""
    tz = dt.tzinfo
    dt_naive = dt.replace(tzinfo=None)
    dt_naive = dt_naive.replace(minute=0, second=0, microsecond=0)
    return safe_localize(dt_naive, tz)


def start_of_day(dt: datetime) -> datetime:
    """Floors to the beginning of the current day (00:00:00)."""
    tz = dt.tzinfo
    dt_naive = dt.replace(tzinfo=None)
    dt_naive = dt_naive.replace(hour=0, minute=0, second=0, microsecond=0)
    return safe_localize(dt_naive, tz)


def start_of_week(dt: datetime, week_start_day: int = 0) -> datetime:
    """Floors to the beginning of the week based on the specified start day.

    0=Monday, ..., 6=Sunday. Defaults to 0 (Monday).
    """
    if week_start_day < 0 or week_start_day > 6:
        raise ValueError("week_start_day must be between 0 and 6 (inclusive)")
    tz = dt.tzinfo
    dt_naive = dt.replace(tzinfo=None)
    dt_naive = dt_naive.replace(hour=0, minute=0, second=0, microsecond=0)
    weekday = dt_naive.weekday()
    if weekday >= week_start_day:
        days_to_subtract = weekday - week_start_day
    else:
        days_to_subtract = (weekday + 7) - week_start_day
    dt_naive = dt_naive - timedelta(days=days_to_subtract)
    return safe_localize(dt_naive, tz)


def start_of_month(dt: datetime) -> datetime:
    """Floors to the beginning of the current month (1st, 00:00:00)."""
    tz = dt.tzinfo
    dt_naive = dt.replace(tzinfo=None)
    dt_naive = dt_naive.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return safe_localize(dt_naive, tz)


def start_of_year(dt: datetime) -> datetime:
    """Floors to the beginning of the current year (Jan 1, 00:00:00)."""
    tz = dt.tzinfo
    dt_naive = dt.replace(tzinfo=None)
    dt_naive = dt_naive.replace(
        month=1, day=1, hour=0, minute=0, second=0, microsecond=0
    )
    return safe_localize(dt_naive, tz)


def start_of_next_second(dt: datetime) -> datetime:
    """Start of the next second."""
    tz = dt.tzinfo
    dt_naive = dt.replace(tzinfo=None)
    dt_naive = dt_naive.replace(microsecond=0) + timedelta(seconds=1)
    return safe_localize(dt_naive, tz)


def start_of_next_minute(dt: datetime) -> datetime:
    """Start of the next minute."""
    tz = dt.tzinfo
    dt_naive = dt.replace(tzinfo=None)
    dt_naive = dt_naive.replace(second=0, microsecond=0) + timedelta(minutes=1)
    return safe_localize(dt_naive, tz)


def start_of_next_hour(dt: datetime) -> datetime:
    """Start of the next hour."""
    tz = dt.tzinfo
    dt_naive = dt.replace(tzinfo=None)
    dt_naive = dt_naive.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    return safe_localize(dt_naive, tz)


def start_of_next_day(dt: datetime) -> datetime:
    """Start of the next day."""
    tz = dt.tzinfo
    dt_naive = dt.replace(tzinfo=None)
    dt_naive = dt_naive.replace(hour=0, minute=0, second=0, microsecond=0)
    dt_naive = dt_naive + timedelta(days=1)
    return safe_localize(dt_naive, tz)


def start_of_next_week(dt: datetime, week_start_day: int = 0) -> datetime:
    """Start of the next week based on the specified start day.

    0=Monday, ..., 6=Sunday. Defaults to 0 (Monday).
    """
    if week_start_day < 0 or week_start_day > 6:
        raise ValueError("week_start_day must be between 0 and 6 (inclusive)")
    tz = dt.tzinfo
    dt_naive = dt.replace(tzinfo=None)
    dt_naive = dt_naive.replace(hour=0, minute=0, second=0, microsecond=0)
    weekday = dt_naive.weekday()
    if weekday < week_start_day:
        days_to_add = week_start_day - weekday
    else:
        days_to_add = 7 - (weekday - week_start_day)
    dt_naive = dt_naive + timedelta(days=days_to_add)
    return safe_localize(dt_naive, tz)


def start_of_next_month(dt: datetime) -> datetime:
    """Start of the next month."""
    tz = dt.tzinfo
    dt_naive = dt.replace(tzinfo=None)
    dt_naive = dt_naive.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if dt_naive.month == 12:
        dt_naive = dt_naive.replace(year=dt_naive.year + 1, month=1)
    else:
        dt_naive = dt_naive.replace(month=dt_naive.month + 1)
    return safe_localize(dt_naive, tz)


def start_of_next_year(dt: datetime) -> datetime:
    """Start of the next year."""
    tz = dt.tzinfo
    dt_naive = dt.replace(tzinfo=None)
    dt_naive = dt_naive.replace(
        year=dt_naive.year + 1,
        month=1,
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    return safe_localize(dt_naive, tz)
