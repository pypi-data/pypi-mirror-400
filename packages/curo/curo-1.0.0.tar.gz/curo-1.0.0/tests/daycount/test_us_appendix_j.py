# tests/daycount/test_us_appendix_j.py
# pylint: disable=C0114, C0116, W0621
# - C0114: missing-module-docstring
# - C0116: missing-function-docstring
# - W0621: redefined-outer-name

import pytest
import pandas as pd
from curo.daycount.us_appendix_j import USAppendixJ
from curo.enums import DayCountTimePeriod, DayCountOrigin

@pytest.fixture
def dc_year():
    return USAppendixJ(time_period=DayCountTimePeriod.YEAR)

@pytest.fixture
def dc_half_year():
    return USAppendixJ(time_period=DayCountTimePeriod.HALF_YEAR)

@pytest.fixture
def dc_quarter():
    return USAppendixJ(time_period=DayCountTimePeriod.QUARTER)

@pytest.fixture
def dc_month():
    return USAppendixJ(time_period=DayCountTimePeriod.MONTH)

@pytest.fixture
def dc_fortnight():
    return USAppendixJ(time_period=DayCountTimePeriod.FORTNIGHT)

@pytest.fixture
def dc_week():
    return USAppendixJ(time_period=DayCountTimePeriod.WEEK)

@pytest.fixture
def dc_day():
    return USAppendixJ(time_period=DayCountTimePeriod.DAY)

def test_compute_factor_year_2023_02_28_to_2024_02_29(dc_year):
    factor = dc_year.compute_factor(
        pd.Timestamp('2023-02-28', tz='UTC'),
        pd.Timestamp('2024-02-29', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(1.0) # 1 year
    assert factor.partial_period_fraction == 0.0
    assert factor.discount_terms_log == ["t = 1", "f = 0", "p = 1"]
    assert str(factor) == "t = 1 : f = 0 : p = 1"
    assert factor.to_folded_string() == "t = 1 : f = 0 : p = 1"

def test_compute_factor_year_2023_05_31_to_2024_06_15(dc_year):
    factor = dc_year.compute_factor(
        pd.Timestamp('2023-05-31', tz='UTC'),
        pd.Timestamp('2024-06-15', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(1.0) # 1 year
    assert factor.partial_period_fraction == pytest.approx(15.0/365.0) # 15 days
    assert str(factor) == "t = 1 : f = 15/365 = 0.04109589 : p = 1"
    assert factor.to_folded_string() == "t = 1 : f = 15/365 = 0.04109589 : p = 1"

def test_compute_factor_half_year_2023_02_28_to_2024_02_29(dc_half_year):
    factor = dc_half_year.compute_factor(
        pd.Timestamp('2023-02-28', tz='UTC'),
        pd.Timestamp('2024-02-29', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(2.0) # 2 half-years
    assert factor.partial_period_fraction == 0.0
    assert str(factor) == "t = 2 : f = 0 : p = 2"
    assert factor.to_folded_string() == "t = 2 : f = 0 : p = 2"

def test_compute_factor_half_year_2023_05_31_to_2024_06_15(dc_half_year):
    factor = dc_half_year.compute_factor(
        pd.Timestamp('2023-05-31', tz='UTC'),
        pd.Timestamp('2024-06-15', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(2.0) # 2 half-years
    assert factor.partial_period_fraction == pytest.approx(15.0/180.0) # 15 days
    assert str(factor) == "t = 2 : f = 15/180 = 0.08333333 : p = 2" #04109589
    assert factor.to_folded_string() == "t = 2 : f = 15/180 = 0.08333333 : p = 2"

def test_compute_factor_quarter_2023_02_28_to_2024_02_29(dc_quarter):
    factor = dc_quarter.compute_factor(
        pd.Timestamp('2023-02-28', tz='UTC'),
        pd.Timestamp('2024-02-29', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(4.0) # 4 quarters
    assert factor.partial_period_fraction == 0.0
    assert str(factor) == "t = 4 : f = 0 : p = 4"
    assert factor.to_folded_string() == "t = 4 : f = 0 : p = 4"

def test_compute_factor_quarter_2023_05_31_to_2024_06_15(dc_quarter):
    factor = dc_quarter.compute_factor(
        pd.Timestamp('2023-05-31', tz='UTC'),
        pd.Timestamp('2024-06-15', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(4.0) # 4 quarters
    assert factor.partial_period_fraction == pytest.approx(15.0/90.0) # 15 days
    assert str(factor) == "t = 4 : f = 15/90 = 0.16666667 : p = 4"
    assert factor.to_folded_string() == "t = 4 : f = 15/90 = 0.16666667 : p = 4"

def test_compute_factor_month_2024_01_31_to_2024_02_29(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2024-01-31', tz='UTC'),
        pd.Timestamp('2024-02-29', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(1.0) # 1 month
    assert factor.partial_period_fraction == 0.0
    assert str(factor) == "t = 1 : f = 0 : p = 12"
    assert factor.to_folded_string() == "t = 1 : f = 0 : p = 12"

def test_compute_factor_month_2023_10_31_to_2024_02_29(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2023-10-31', tz='UTC'), # month-end
        pd.Timestamp('2024-02-29', tz='UTC')  # month-end leap year
    )
    assert factor.primary_period_fraction == pytest.approx(4.0) # 4 months
    assert factor.partial_period_fraction == 0.0
    assert str(factor) == "t = 4 : f = 0 : p = 12"
    assert factor.to_folded_string() == "t = 4 : f = 0 : p = 12"

def test_compute_factor_month_2024_10_31_to_2025_02_28(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2024-10-31', tz='UTC'), # month-end
        pd.Timestamp('2025-02-28', tz='UTC')  # month-end non leap year
    )
    assert factor.primary_period_fraction == pytest.approx(4.0) # 4 months
    assert factor.partial_period_fraction == 0.0
    assert str(factor) == "t = 4 : f = 0 : p = 12"
    assert factor.to_folded_string() == "t = 4 : f = 0 : p = 12"

def test_compute_factor_month_2024_10_15_to_2025_03_31(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2024-10-15', tz='UTC'),
        pd.Timestamp('2025-03-31', tz='UTC')
    )
    # 2024-10-31 <- 2025-03-31 = 5 months
    # 2024-10-15 <- 2024-10-31 = 16 days
    assert factor.primary_period_fraction == pytest.approx(5.0) # 5 months
    assert factor.partial_period_fraction == pytest.approx(16.0/30.0) # 16 days
    assert str(factor) == "t = 5 : f = 16/30 = 0.53333333 : p = 12"
    assert factor.to_folded_string() == "t = 5 : f = 16/30 = 0.53333333 : p = 12"

def test_compute_factor_month_2026_01_10_to_2026_02_15(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2026-01-10', tz='UTC'),
        pd.Timestamp('2026-02-15', tz='UTC')
    )
    # 2026-01-15 <- 2026-02-15 = 1 month
    # 2026-01-10 <- 2026-01-15 = 5 days
    assert factor.primary_period_fraction == pytest.approx(1.0) # 1 month
    assert factor.partial_period_fraction == pytest.approx(5.0 / 30.0)
    assert str(factor) == "t = 1 : f = 5/30 = 0.16666667 : p = 12"
    assert factor.to_folded_string() == "t = 1 : f = 5/30 = 0.16666667 : p = 12"

def test_compute_factor_month_2026_01_10_to_2026_03_15(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2026-01-10', tz='UTC'),
        pd.Timestamp('2026-03-15', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(2.0) # 2 months
    assert factor.partial_period_fraction == pytest.approx(5.0 / 30.0)
    assert str(factor) == "t = 2 : f = 5/30 = 0.16666667 : p = 12"
    assert factor.to_folded_string() == "t = 2 : f = 5/30 = 0.16666667 : p = 12"

def test_compute_factor_month_2028_01_10_to_2028_02_29(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2028-01-10', tz='UTC'),
        pd.Timestamp('2028-02-29', tz='UTC')
    )
    # 2028-01-31 <- 2028-02-29 = 1 month
    # 2028-01-10 <- 2028-01-31 = 21 days
    assert factor.primary_period_fraction == pytest.approx(1.0) # 1 month
    assert factor.partial_period_fraction == pytest.approx(21.0 / 30.0)
    assert str(factor) == "t = 1 : f = 21/30 = 0.70000000 : p = 12"
    assert factor.to_folded_string() == "t = 1 : f = 21/30 = 0.70000000 : p = 12"

def test_compute_factor_month_2025_03_29_to_2025_06_30(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2025-03-29', tz='UTC'),
        pd.Timestamp('2025-06-30', tz='UTC') # month-end
    )
    # 2025-05-31 <- 2025-06-30 = 1 month
    # 2025-04-30 <- 2025-05-31 = 1 month
    # 2025-03-31 <- 2025-04-30 = 1 month
    # 2025-03-29 <- 2025-03-31 = 2 days
    assert factor.primary_period_fraction == pytest.approx(3.0) # 3 months
    assert factor.partial_period_fraction == pytest.approx(2.0 / 30.0)
    assert str(factor) == "t = 3 : f = 2/30 = 0.06666667 : p = 12"
    assert factor.to_folded_string() == "t = 3 : f = 2/30 = 0.06666667 : p = 12"

def test_compute_factor_month_2028_01_10_to_2028_02_15(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2028-01-10', tz='UTC'),
        pd.Timestamp('2028-02-15', tz='UTC')
    )
    # 2028-01-15 <- 2028-02-15 = 1 month
    # 2028-01-10 <- 2028-01-15 = 5 days
    assert factor.primary_period_fraction == pytest.approx(1.0) # 1 month
    assert factor.partial_period_fraction == pytest.approx(5.0 / 30.0)
    assert str(factor) == "t = 1 : f = 5/30 = 0.16666667 : p = 12"
    assert factor.to_folded_string() == "t = 1 : f = 5/30 = 0.16666667 : p = 12"

def test_compute_factor_month_2026_01_10_to_2026_04_15(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2026-01-10', tz='UTC'),
        pd.Timestamp('2026-04-15', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(3.0) # 3 months
    assert factor.partial_period_fraction == pytest.approx(5.0 / 30.0)
    assert str(factor) == "t = 3 : f = 5/30 = 0.16666667 : p = 12"
    assert factor.to_folded_string() == "t = 3 : f = 5/30 = 0.16666667 : p = 12"

def test_compute_factor_fortnight_2025_12_06_to_2026_01_03(dc_fortnight):
    factor = dc_fortnight.compute_factor(
        pd.Timestamp('2025-12-06', tz='UTC'),
        pd.Timestamp('2026-01-03', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(2.0) # 2 fortnights
    assert factor.partial_period_fraction == 0.0
    assert str(factor) == "t = 2 : f = 0 : p = 26"
    assert factor.to_folded_string() == "t = 2 : f = 0 : p = 26"

def test_compute_factor_fortnight_2025_12_01_to_2026_01_03(dc_fortnight):
    factor = dc_fortnight.compute_factor(
        pd.Timestamp('2025-12-01', tz='UTC'),
        pd.Timestamp('2026-01-03', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(2.0) # 2 fortnights
    assert factor.partial_period_fraction == pytest.approx(5.0/15.0) # 5 days
    assert str(factor) == "t = 2 : f = 5/15 = 0.33333333 : p = 26"
    assert factor.to_folded_string() == "t = 2 : f = 5/15 = 0.33333333 : p = 26"

def test_compute_factor_week_2025_12_06_to_2026_01_03(dc_week):
    factor = dc_week.compute_factor(
        pd.Timestamp('2025-12-06', tz='UTC'),
        pd.Timestamp('2026-01-03', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(4.0) # 4 weeks
    assert factor.partial_period_fraction == 0.0
    assert str(factor) == "t = 4 : f = 0 : p = 52"
    assert factor.to_folded_string() == "t = 4 : f = 0 : p = 52"

def test_compute_factor_week_2025_12_01_to_2026_01_03(dc_week):
    factor = dc_week.compute_factor(
        pd.Timestamp('2025-12-01', tz='UTC'),
        pd.Timestamp('2026-01-03', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(4.0) # 4 weeks
    assert factor.partial_period_fraction == pytest.approx(5.0/7.0) # 5 days
    assert str(factor) == "t = 4 : f = 5/7 = 0.71428571 : p = 52"
    assert factor.to_folded_string() == "t = 4 : f = 5/7 = 0.71428571 : p = 52"

def test_compute_factor_day_2026_01_10_to_2026_01_25(dc_day):
    factor = dc_day.compute_factor(
        pd.Timestamp('2026-01-10', tz='UTC'),
        pd.Timestamp('2026-01-25', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.0)
    assert factor.partial_period_fraction == pytest.approx(15/365)
    assert str(factor) == "t = 0 : f = 15/365 = 0.04109589 : p = 365"
    assert factor.to_folded_string() == "t = 0 : f = 15/365 = 0.04109589 : p = 365"

def test_compute_factor_negative_period(dc_month):
    with pytest.raises(ValueError, match="end must be after start"):
        dc_month.compute_factor(
            pd.Timestamp('2026-02-01', tz='UTC'),
            pd.Timestamp('2026-01-01', tz='UTC')
        )

def test_compute_factor_same_day(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2026-01-10', tz='UTC'),
        pd.Timestamp('2026-01-10', tz='UTC')
    )
    assert factor.primary_period_fraction == 0.0
    assert str(factor) == "t = 0 : f = 0 : p = 12"
    assert factor.to_folded_string() == "t = 0 : f = 0 : p = 12"

def test_default_instance():
    dc = USAppendixJ()
    assert dc.time_period == DayCountTimePeriod.MONTH
    assert dc.day_count_origin == DayCountOrigin.DRAWDOWN
    assert dc.use_post_dates is True
    assert dc.include_non_financing_flows is True
    assert dc.use_xirr_method is True
