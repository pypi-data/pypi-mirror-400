# tests/test_utils.py
# pylint: disable=C0114, C0116, W0621
# - C0114: missing-module-docstring
# - C0116: missing-function-docstring
# - W0621: redefined-outer-name

from datetime import datetime, date, timezone
from unittest.mock import Mock
import pytest
import pandas as pd
from curo import Frequency, ValidationError
from curo.utils import (
    actual_days,
    roll_month,
    roll_day,
    roll_date,
    has_month_end_day,
    to_timestamp,
    gauss_round
    )

@pytest.fixture
def base_date():
    return pd.Timestamp('2025-01-15', tz='UTC')

# Test suite for actual days
def test_actual_days_same_date(base_date):
    """Test actual_days with the same start and end date."""
    result = actual_days(base_date, base_date)
    assert result == 0

def test_actual_days_leap_year():
    """Test actual_days across a leap year period."""
    result = actual_days(
        pd.Timestamp('2024-01-31', tz='UTC'),
        pd.Timestamp('2024-02-29', tz='UTC')
    )
    assert result == 29

def test_actual_days_non_leap_year():
    """Test actual_days across a non-leap year period."""
    result = actual_days(
        pd.Timestamp('2025-01-31', tz='UTC'),
        pd.Timestamp('2025-02-28', tz='UTC')
    )
    assert result == 28

def test_actual_days_reversed():
    """Test actual_days with end before start (should return absolute days)."""
    result = actual_days(
        pd.Timestamp('2024-02-29', tz='UTC'),
        pd.Timestamp('2024-01-31', tz='UTC')
    )
    assert result == 29

def test_actual_days_naive_timestamps():
    """Test actual_days with naive timestamps."""
    result = actual_days(
        pd.Timestamp('2025-01-01'),
        pd.Timestamp('2025-01-03')
    )
    assert result == 2

def test_actual_days_different_timezones():
    """Test actual_days with different timezones, counting calendar days."""
    result = actual_days(
        pd.Timestamp('2025-01-01 12:00:00', tz='US/Pacific'),
        pd.Timestamp('2025-01-03 00:00:00', tz='UTC')
    )
    # Timezone differences don't affect day count
    assert result == 2

def test_actual_days_same_day_different_times():
    """Test actual_days with same day but different times."""
    result = actual_days(
        pd.Timestamp('2025-01-01 00:00:00', tz='UTC'),
        pd.Timestamp('2025-01-01 23:59:59', tz='UTC')
    )
    # Same day, no full day completed
    assert result == 0

def test_actual_days_cross_year():
    """Test actual_days across year boundary."""
    result = actual_days(
        pd.Timestamp('2024-12-31', tz='UTC'),
        pd.Timestamp('2025-01-02', tz='UTC')
    )
    assert result == 2

def test_actual_days_invalid_input_types():
    """Test actual_days with invalid input types raises TypeError."""
    invalid_inputs = [
        ('2025-01-01', pd.Timestamp('2025-01-02')),  # String
        (pd.Timestamp('2025-01-01'), '2025-01-02'),  # String
        (datetime(2025, 1, 1), pd.Timestamp('2025-01-02')),  # datetime
        (pd.Timestamp('2025-01-01'), 123),  # Integer
    ]
    for start, end in invalid_inputs:
        with pytest.raises(TypeError, match="start and end must be pd.Timestamp"):
            actual_days(start, end)

# Test suite for roll_month
def test_roll_month_forward(base_date):
    result = roll_month(base_date, months=2, day=10)
    assert result == pd.Timestamp('2025-03-10', tz='UTC')

def test_roll_month_backward(base_date):
    result = roll_month(base_date, months=-1, day=20)
    assert result == pd.Timestamp('2024-12-20', tz='UTC')

def test_roll_month_invalid_day(base_date):
    # February 2025 has 28 days, so day=31 should cap at month-end (Feb 28)
    result = roll_month(base_date, months=1, day=31)
    assert result == pd.Timestamp('2025-02-28', tz='UTC')

def test_roll_month_zero_months(base_date):
    result = roll_month(base_date, months=0, day=5)
    assert result == pd.Timestamp('2025-01-05', tz='UTC')

def test_roll_month_leap_year():
    # Test rolling to February in a leap year (2024)
    date = pd.Timestamp('2024-01-15', tz='UTC')
    result = roll_month(date, months=1, day=29)
    assert result == pd.Timestamp('2024-02-29', tz='UTC')

def test_roll_month_invalid_day_non_leap():
    # February 2023 is not a leap year, so day=29 should cap at Feb 28
    date = pd.Timestamp('2023-01-15', tz='UTC')
    result = roll_month(date, months=1, day=29)
    assert result == pd.Timestamp('2023-02-28', tz='UTC')

# Test suite for roll_day
def test_roll_day_forward(base_date):
    result = roll_day(base_date, days=5)
    assert result == pd.Timestamp('2025-01-20', tz='UTC')

def test_roll_day_backward(base_date):
    result = roll_day(base_date, days=-10)
    assert result == pd.Timestamp('2025-01-05', tz='UTC')

def test_roll_day_zero(base_date):
    result = roll_day(base_date, days=0)
    assert result == pd.Timestamp('2025-01-15', tz='UTC')

# Test suite for roll_date
@pytest.fixture
def mock_roll_functions(monkeypatch):
    """Mock roll_day and roll_month to return a pd.Timestamp."""
    mock_roll_day = Mock(return_value=pd.Timestamp('2025-12-30 00:00:00', tz='UTC'))
    mock_roll_month = Mock(return_value=pd.Timestamp('2025-12-30 00:00:00', tz='UTC'))
    monkeypatch.setattr("curo.utils.roll_day", mock_roll_day)
    monkeypatch.setattr("curo.utils.roll_month", mock_roll_month)
    return mock_roll_day, mock_roll_month

def test_roll_date_weekly(mock_roll_functions):
    """Test roll_date with WEEKLY frequency."""
    mock_roll_day, _ = mock_roll_functions
    date = pd.Timestamp('2025-01-01 14:30:00', tz='UTC')
    result = roll_date(date, Frequency.WEEKLY, day=15)

    # Verify roll_day called with correct arguments
    mock_roll_day.assert_called_once_with(date, 7)
    assert isinstance(result, pd.Timestamp)
    assert result == pd.Timestamp('2025-12-30 00:00:00', tz='UTC')
    assert result.tzinfo == timezone.utc
    assert result.hour == 0

def test_roll_date_fortnightly(mock_roll_functions):
    """Test roll_date with FORTNIGHTLY frequency."""
    mock_roll_day, _ = mock_roll_functions
    date = pd.Timestamp('2025-01-01 14:30:00', tz='UTC')
    result = roll_date(date, Frequency.FORTNIGHTLY, day=15)

    # Verify roll_day called with correct arguments
    mock_roll_day.assert_called_once_with(date, 14)
    assert isinstance(result, pd.Timestamp)
    assert result == pd.Timestamp('2025-12-30 00:00:00', tz='UTC')
    assert result.tzinfo == timezone.utc
    assert result.hour == 0

def test_roll_date_monthly(mock_roll_functions):
    """Test roll_date with MONTHLY frequency."""
    _, mock_roll_month = mock_roll_functions
    date = pd.Timestamp('2025-01-01 14:30:00', tz='UTC')
    result = roll_date(date, Frequency.MONTHLY, day=15)

    # Verify roll_month called with correct arguments
    mock_roll_month.assert_called_once_with(date, 1, 15)
    assert isinstance(result, pd.Timestamp)
    assert result == pd.Timestamp('2025-12-30 00:00:00', tz='UTC')
    assert result.tzinfo == timezone.utc
    assert result.hour == 0

def test_roll_date_quarterly(mock_roll_functions):
    """Test roll_date with QUARTERLY frequency."""
    _, mock_roll_month = mock_roll_functions
    date = pd.Timestamp('2025-01-01 14:30:00', tz='UTC')
    result = roll_date(date, Frequency.QUARTERLY, day=15)

    # Verify roll_month called with correct arguments
    mock_roll_month.assert_called_once_with(date, 3, 15)
    assert isinstance(result, pd.Timestamp)
    assert result == pd.Timestamp('2025-12-30 00:00:00', tz='UTC')
    assert result.tzinfo == timezone.utc
    assert result.hour == 0

def test_roll_date_half_yearly(mock_roll_functions):
    """Test roll_date with HALF_YEARLY frequency."""
    _, mock_roll_month = mock_roll_functions
    date = pd.Timestamp('2025-01-01 14:30:00', tz='UTC')
    result = roll_date(date, Frequency.HALF_YEARLY, day=15)

    # Verify roll_month called with correct arguments
    mock_roll_month.assert_called_once_with(date, 6, 15)
    assert isinstance(result, pd.Timestamp)
    assert result == pd.Timestamp('2025-12-30 00:00:00', tz='UTC')
    assert result.tzinfo == timezone.utc
    assert result.hour == 0

def test_roll_date_yearly(mock_roll_functions):
    """Test roll_date with YEARLY frequency."""
    _, mock_roll_month = mock_roll_functions
    date = pd.Timestamp('2025-01-01 14:30:00', tz='UTC')
    result = roll_date(date, Frequency.YEARLY, day=15)

    # Verify roll_month called with correct arguments
    mock_roll_month.assert_called_once_with(date, 12, 15)
    assert isinstance(result, pd.Timestamp)
    assert result == pd.Timestamp('2025-12-30 00:00:00', tz='UTC')
    assert result.tzinfo == timezone.utc
    assert result.hour == 0

def test_roll_date_invalid_frequency():
    """Test roll_date with an invalid frequency raises ValueError."""
    date = pd.Timestamp('2025-01-01')
    with pytest.raises(ValueError, match="Unknown frequency: INVALID"):
        class InvalidFrequency:
            """Simulate an invalid Frequency value"""
            def __eq__(self, other):
                return False
            def __str__(self):
                return "INVALID"
        roll_date(date, InvalidFrequency(), day=15)

def test_roll_date_naive_timestamp(mock_roll_functions):
    """Test roll_date with a naive timestamp preserves naive state."""
    _, mock_roll_month = mock_roll_functions
    mock_roll_month.return_value = pd.Timestamp('2025-12-30 00:00:00')  # Naive
    date = pd.Timestamp('2025-01-01 14:30:00')  # Naive
    result = roll_date(date, Frequency.MONTHLY, day=15)

    mock_roll_month.assert_called_once_with(date, 1, 15)
    assert isinstance(result, pd.Timestamp)
    assert result.tzinfo is None
    assert result.hour == 0

def test_roll_date_edge_case_day(mock_roll_functions):
    """Test roll_date with edge case day values."""
    _, mock_roll_month = mock_roll_functions
    date = pd.Timestamp('2025-01-01', tz='UTC')

    # Test day=0, negative day, and high day (handled by roll_month)
    for day in [0, -1, 31]:
        result = roll_date(date, Frequency.MONTHLY, day=day)
        mock_roll_month.assert_called_with(date, 1, day)
        assert isinstance(result, pd.Timestamp)
        assert result.tzinfo == timezone.utc
        assert result.hour == 0
    assert mock_roll_month.call_count == 3

def test_roll_date_leap_year_day(mock_roll_functions):
    """Test roll_date with day=29 for leap year handling."""
    _, mock_roll_month = mock_roll_functions
    date = pd.Timestamp('2024-02-29', tz='UTC')  # Leap year
    result = roll_date(date, Frequency.MONTHLY, day=29)

    mock_roll_month.assert_called_once_with(date, 1, 29)
    assert isinstance(result, pd.Timestamp)
    assert result.tzinfo == timezone.utc
    assert result.hour == 0

# Test suite for to_timestamp
def test_to_timestamp_none():
    """Test when input is None."""
    result = to_timestamp(None)
    assert result is None

def test_to_timestamp_naive_timestamp():
    """Test with a naive pd.Timestamp."""
    input_dt = pd.Timestamp('2025-12-30 14:30:00')
    result = to_timestamp(input_dt)
    expected = pd.Timestamp('2025-12-30 00:00:00', tz='UTC')
    assert result == expected
    assert result.tzinfo == timezone.utc
    assert result.hour == 0
    assert result.minute == 0
    assert result.second == 0

def test_to_timestamp_aware_non_utc_timestamp():
    """Test with an aware pd.Timestamp in a non-UTC timezone."""
    input_dt = pd.Timestamp('2025-12-30 14:30:00', tz='US/Pacific')
    result = to_timestamp(input_dt)
    expected = pd.Timestamp('2025-12-30 00:00:00', tz='UTC')
    assert result == expected
    assert result.tzinfo == timezone.utc
    assert result.hour == 0

def test_to_timestamp_aware_utc_timestamp():
    """Test with an aware pd.Timestamp already in UTC."""
    input_dt = pd.Timestamp('2025-12-30 14:30:00', tz='UTC')
    result = to_timestamp(input_dt)
    expected = pd.Timestamp('2025-12-30 00:00:00', tz='UTC')
    assert result == expected
    assert result.tzinfo == timezone.utc
    assert result.hour == 0

def test_to_timestamp_datetime_with_time():
    """Test with a datetime.datetime with time component."""
    input_dt = datetime(2025, 12, 30, 14, 30)
    result = to_timestamp(input_dt)
    expected = pd.Timestamp('2025-12-30 00:00:00', tz='UTC')
    assert result == expected
    assert result.tzinfo == timezone.utc
    assert result.hour == 0

def test_to_timestamp_datetime_midnight():
    """Test with a datetime.datetime at midnight."""
    input_dt = datetime(2025, 12, 30, 0, 0)
    result = to_timestamp(input_dt)
    expected = pd.Timestamp('2025-12-30 00:00:00', tz='UTC')
    assert result == expected
    assert result.tzinfo == timezone.utc
    assert result.hour == 0

def test_to_timestamp_date():
    """Test with a datetime.date."""
    input_dt = date(2025, 12, 30)
    result = to_timestamp(input_dt)
    expected = pd.Timestamp('2025-12-30 00:00:00', tz='UTC')
    assert result == expected
    assert result.tzinfo == timezone.utc
    assert result.hour == 0

def test_to_timestamp_invalid_type():
    """Test with an invalid input type raises ValidationError."""
    invalid_inputs = ['2025-12-30', 123, 3.14, [2025, 12, 30]]
    for invalid_input in invalid_inputs:
        with pytest.raises(
            ValidationError,
            match="Date must be pd.Timestamp, datetime.datetime, or datetime.date"):
            to_timestamp(invalid_input)

# Test suite for has_month_end_day
def test_has_month_end_day_true():
    date = pd.Timestamp('2025-01-31', tz='UTC')
    assert has_month_end_day(date) is True

def test_has_month_end_day_false():
    date = pd.Timestamp('2025-01-30', tz='UTC')
    assert has_month_end_day(date) is False

def test_has_month_end_day_february_leap():
    date = pd.Timestamp('2024-02-29', tz='UTC')  # 2024 is a leap year
    assert has_month_end_day(date) is True

# Test suite for gauss_round
def test_gauss_round_halfway_even():
    assert gauss_round(2.5, precision=0) == 2.0  # Rounds to nearest even (2)
    assert gauss_round(3.5, precision=0) == 4.0  # Rounds to nearest even (4)

def test_gauss_round_halfway_odd():
    assert gauss_round(1.5, precision=0) == 2.0  # Rounds up (1 is odd)
    assert gauss_round(4.5, precision=0) == 4.0  # Rounds down (4 is even)

def test_gauss_round_precision():
    assert gauss_round(2.345, precision=2) == 2.34  # Rounds to 2.34 (even)
    assert gauss_round(2.355, precision=2) == 2.36  # Rounds to 2.36 (odd)

def test_gauss_round_negative_precision():
    assert gauss_round(123.45, precision=-1) == 120.0  # Rounds to nearest 10
    assert gauss_round(125.0, precision=-1) == 120.0  # Rounds to nearest even 10

def test_gauss_round_negative_precision_hundreds():
    assert gauss_round(1234.56, precision=-2) == 1200.0  # Rounds to nearest 100, even
    assert gauss_round(1250.0, precision=-2) == 1200.0  # Rounds to nearest even 100

def test_gauss_round_large_number():
    assert gauss_round(123456.78, precision=-3) == 123000.0  # Rounds to nearest 1000
