"""
Utility functions used internally for date manipulation and numerical 
rounding in financial calculations.
"""

from typing import Union, Optional
from datetime import datetime
# Use dt_module to access datetime.date without importing 'date', avoiding
# Pylint W0621:redefined-outer-name due to a conflicting 'date' in scope.
import datetime as dt_module
import numpy as np
import pandas as pd
from curo.enums import Frequency
from curo.exceptions import ValidationError


def actual_days(start: pd.Timestamp, end: pd.Timestamp) -> int:
    """
    Returns the absolute number of days between two dates (inclusive of start,
    exclusive of end), regardless of date order. Times and timezones are ignored
    by normalizing to calendar dates.
    Args:
        start: The start date (pd.Timestamp).
        end: The end date (pd.Timestamp).
    Returns:
        int: The absolute number of days between start and end.
    Raises:
        TypeError: If start or end is not a pd.Timestamp.
    """
    if not (isinstance(start, pd.Timestamp) and isinstance(end, pd.Timestamp)):
        raise TypeError("start and end must be pd.Timestamp")
    start_date = start.normalize().date()
    end_date = end.normalize().date()
    return abs((end_date - start_date).days)

def roll_month(date: pd.Timestamp, months: int, day: int) -> pd.Timestamp:
    """
    Rolls a date by the specified number of months, adjusting to a preferred day.

    Args:
        date: The input date to roll (pd.Timestamp).
        months: Number of months to roll; positive for forward, negative for backward (int).
        day: Preferred day of the month for the resulting date; capped at month-end if
            invalid (int).

    Returns:
        pd.Timestamp: The rolled date, preserving the input timezone and normalized to midnight.
    """
    # Roll by months using DateOffset
    new_date = date + pd.offsets.DateOffset(months=months)
    try:
        return new_date.replace(day=day)
    except ValueError:
        # If day is invalid, use the last day of the month
        month_end = new_date + pd.offsets.MonthEnd(0)
        return month_end

def roll_day(date: pd.Timestamp, days: int) -> pd.Timestamp:
    """
    Rolls a date by the specified number of days.

    Args:
        date: The input date to roll (pd.Timestamp).
        days: Number of days to roll; positive for forward, 
            negative for backward (int).

    Returns:
        pd.Timestamp: The rolled date, preserving the input 
            timezone and normalized to midnight.
    """
    return date + pd.Timedelta(days=days)

def roll_date(date: pd.Timestamp, frequency: Frequency, day: int) -> pd.Timestamp:
    """
    Rolls a date forward by the frequency implicit period, adjusting to a 
    preferred day.

    Args:
        date: The input date to roll (pd.Timestamp).
        frequency: The implicit interval to roll date forward (Frequency).
        day: Preferred day of the month for the resulting date; capped at month-end if
            invalid (int). Note: ignored when frequency WEEKLY or FORTNIGHTLY.

    Returns:
        pd.Timestamp: The rolled date, preserving the input timezone and normalized to midnight.
    """
    if frequency == Frequency.WEEKLY:
        date = roll_day(date, 7)
    elif frequency == Frequency.FORTNIGHTLY:
        date = roll_day(date, 14)
    elif frequency == Frequency.MONTHLY:
        date = roll_month(date, 1, day)
    elif frequency == Frequency.QUARTERLY:
        date = roll_month(date, 3, day)
    elif frequency == Frequency.HALF_YEARLY:
        date = roll_month(date, 6, day)
    elif frequency == Frequency.YEARLY:
        date = roll_month(date, 12, day)
    else:
        raise ValueError(f"Unknown frequency: {frequency}")
    return date

def to_timestamp(
    dt: Optional[Union[pd.Timestamp, datetime, dt_module.date]]
    ) -> Optional[pd.Timestamp]:
    """
    Converts a date input to a pd.Timestamp normalized to midnight UTC.

    Args:
        dt: A pd.Timestamp, datetime.datetime, or datetime.date. If None, returns None.

    Returns:
        pd.Timestamp: A UTC timestamp with time set to midnight (00:00:00), or None.

    Raises:
        ValidationError: If dt is not a supported type.
    """
    if dt is None:
        return None
    if isinstance(dt, pd.Timestamp):
        return (dt.normalize().tz_localize('UTC')
                if dt.tz is None else dt.tz_convert('UTC').normalize())
    if isinstance(dt, (datetime, dt_module.date)):
        return pd.Timestamp(dt).tz_localize('UTC').normalize()
    raise ValidationError(
        "Date must be pd.Timestamp, datetime.datetime, or datetime.date"
    )

def has_month_end_day(date: pd.Timestamp) -> bool:
    """
    Checks if a date is the last day of its month.

    Args:
        date: The date to check (pd.Timestamp).

    Returns:
        bool: True if the date is the last day of the month,
            False otherwise.
    """
    return date == (date + pd.offsets.MonthEnd(0))

def gauss_round(num: float, precision: int = 0) -> float:
    """
    Performs Gaussian (bankers') rounding to the nearest even number to avoid 
    statistical bias.

    Unlike standard rounding, which biases upward, Gaussian rounding selects 
    the nearest even number when a value is exactly halfway between two numbers
    (e.g., 2.5 rounds to 2, 3.5 to 4).

    Note:
        Ported and modified from JavaScript source by 
        Tim Down[](http://stackoverflow.com/a/3109234).

    Args:
        num: The number to round (float).
        precision: Number of decimal places; can be positive or 
            negative (int, optional). Defaults to 0.

    Returns:
        float: The number rounded to the specified precision.
    """
    m = 10 ** precision
    n = np.round(num * m, 8)
    i = np.floor(n)
    f = n - i
    e = 1e-8
    r = i if f > 0.5 - e and f < 0.5 + e and int(i) % 2 == 0 else np.round(n)
    return r / m
