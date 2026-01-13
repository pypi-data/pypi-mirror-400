# tests/daycount/test_uk_conc_app.py
# pylint: disable=C0114, C0116, W0621
# - C0114: missing-module-docstring
# - C0116: missing-function-docstring
# - W0621: redefined-outer-name

import pytest
import pandas as pd
from curo.daycount.uk_conc_app import UKConcApp
from curo.enums import DayCountTimePeriod, DayCountOrigin

@pytest.fixture
def dc_month():
    return UKConcApp(time_period=DayCountTimePeriod.MONTH)

@pytest.fixture
def dc_week():
    return UKConcApp(time_period=DayCountTimePeriod.WEEK)

@pytest.fixture
def dc_secured_month():
    return UKConcApp(is_secured_on_land=True, time_period=DayCountTimePeriod.MONTH)

@pytest.fixture
def dc_secured_week():
    return UKConcApp(is_secured_on_land=True, time_period=DayCountTimePeriod.WEEK)

@pytest.fixture
def dc_secured_single_week():
    return UKConcApp(
        is_secured_on_land=True,
        has_single_payment=True,
        time_period=DayCountTimePeriod.WEEK)

def test_compute_factor_month_time_period(dc_month):
    assert dc_month.time_period == DayCountTimePeriod.MONTH

def test_compute_factor_month_2025_01_31_to_2025_02_28(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2025-01-31', tz='UTC'),
        pd.Timestamp('2025-02-28', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.08333333333333333)
    assert str(factor) == "f = 1/12 = 0.08333333"
    assert factor.to_folded_string() == "f = 1/12 = 0.08333333"

def test_compute_factor_month_2025_01_12_to_2025_02_15(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2025-01-12', tz='UTC'),
        pd.Timestamp('2025-02-15', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.0915525114155251)
    assert str(factor) == "f = 1/12 + 3/365 = 0.09155251"
    assert factor.to_folded_string() == "f = 1/12 + 3/365 = 0.09155251"

def test_compute_factor_month_2023_12_15_to_2024_02_29(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2023-12-15', tz='UTC'),
        pd.Timestamp('2024-02-29', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.20491803278688525)
    assert str(factor) == "f = 2/12 + 14/366 = 0.20491803"
    assert factor.to_folded_string() == "f = 2/12 + 14/366 = 0.20491803"

def test_compute_factor_month_2025_02_26_to_2025_02_26(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2025-02-26', tz='UTC'),
        pd.Timestamp('2025-02-26', tz='UTC')
    )
    assert factor.primary_period_fraction == 0.0
    assert str(factor) == "f = 0 = 0.00000000"
    assert factor.to_folded_string() == "f = 0 = 0.00000000"

def test_compute_factor_month_2024_12_25_to_2025_02_05(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2024-11-25', tz='UTC'),
        pd.Timestamp('2025-01-05', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(1/12 + 6/366 + 5/365)
    assert str(factor) == "f = 1/12 + 6/366 + 5/365 = 0.11342541"
    assert factor.to_folded_string() == "f = 1/12 + 6/366 + 5/365 = 0.11342541"

def test_compute_factor_week_time_period(dc_week):
    assert dc_week.time_period == DayCountTimePeriod.WEEK

def test_compute_factor_week_2025_01_31_to_2025_02_28(dc_week):
    factor = dc_week.compute_factor(
        pd.Timestamp('2025-01-31', tz='UTC'),
        pd.Timestamp('2025-02-28', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.07692307692307693)
    assert str(factor) == "f = 4/52 = 0.07692308"
    assert factor.to_folded_string() == "f = 4/52 = 0.07692308"

def test_compute_factor_week_2023_01_01_to_2024_01_14(dc_week):
    factor = dc_week.compute_factor(
        pd.Timestamp('2023-01-01', tz='UTC'),
        pd.Timestamp('2024-01-14', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(1.0384615384615385)
    assert str(factor) == "f = 1 + 2/52 = 1.03846154"
    assert factor.to_folded_string() == "f = 1 + 2/52 = 1.03846154"

def test_compute_factor_week_2024_01_12_to_2024_01_30(dc_week):
    factor = dc_week.compute_factor(
        pd.Timestamp('2024-01-12', tz='UTC'),
        pd.Timestamp('2024-01-30', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.04939050021017234)
    assert str(factor) == "f = 2/52 + 4/366 = 0.04939050"
    assert factor.to_folded_string() == "f = 2/52 + 4/366 = 0.04939050"

def test_compute_factor_secured_month_2025_01_31_to_2025_02_28(dc_secured_month):
    factor = dc_secured_month.compute_factor(
        pd.Timestamp('2025-01-31', tz='UTC'),
        pd.Timestamp('2025-02-28', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.08333333333333333)
    assert str(factor) == "f = 1/12 = 0.08333333"
    assert factor.to_folded_string() == "f = 1/12 = 0.08333333"

def test_compute_factor_secured_month_2025_01_31_to_2031_02_28(dc_secured_month):
    factor = dc_secured_month.compute_factor(
        pd.Timestamp('2025-01-31', tz='UTC'),
        pd.Timestamp('2031-02-28', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(6.083333333333333)
    assert str(factor) == "f = 6 + 1/12 = 6.08333333"
    assert factor.to_folded_string() == "f = 6 + 1/12 = 6.08333333"

def test_compute_factor_secured_month_2024_02_29_to_2024_03_07(dc_secured_month):
    factor = dc_secured_month.compute_factor(
        pd.Timestamp('2024-02-29', tz='UTC'),
        pd.Timestamp('2024-03-07', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.019125683060109300)
    assert str(factor) == "f = 7/366 = 0.01912568"
    assert factor.to_folded_string() == "f = 7/366 = 0.01912568"

def test_compute_factor_secured_week_2025_01_31_to_2025_02_28(dc_secured_week):
    factor = dc_secured_week.compute_factor(
        pd.Timestamp('2025-01-31', tz='UTC'),
        pd.Timestamp('2025-02-28', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.07692307692307693)
    assert str(factor) == "f = 4/52 = 0.07692308"
    assert factor.to_folded_string() == "f = 4/52 = 0.07692308"

def test_compute_factor_secured_week_2025_01_31_to_2031_02_28(dc_secured_week):
    factor = dc_secured_week.compute_factor(
        pd.Timestamp('2025-01-31', tz='UTC'),
        pd.Timestamp('2031-02-28', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(6.096153846153846)
    assert str(factor) == "f = 6 + 5/52 = 6.09615385"
    assert factor.to_folded_string() == "f = 6 + 5/52 = 6.09615385"

def test_compute_factor_secured_week_2024_02_29_to_2024_03_07(dc_secured_week):
    factor = dc_secured_week.compute_factor(
        pd.Timestamp('2024-02-29', tz='UTC'),
        pd.Timestamp('2024-03-07', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.019230769230769232)
    assert str(factor) == "f = 1/52 = 0.01923077"
    assert factor.to_folded_string() == "f = 1/52 = 0.01923077"

def test_compute_factor_secured_single_week_2025_01_31_to_2025_02_28(dc_secured_single_week):
    factor = dc_secured_single_week.compute_factor(
        pd.Timestamp('2025-01-31', tz='UTC'),
        pd.Timestamp('2025-02-28', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.08333333333333333)
    assert str(factor) == "f = 1/12 = 0.08333333"
    assert factor.to_folded_string() == "f = 1/12 = 0.08333333"

def test_compute_factor_secured_single_week_2024_01_31_to_2024_02_28(dc_secured_single_week):
    factor = dc_secured_single_week.compute_factor(
        pd.Timestamp('2024-01-31', tz='UTC'),
        pd.Timestamp('2024-02-28', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.08333333333333333)
    assert str(factor) == "f = 1/12 = 0.08333333"
    assert factor.to_folded_string() == "f = 1/12 = 0.08333333"

def test_compute_factor_secured_single_week_2024_01_31_to_2024_02_29(dc_secured_single_week):
    factor = dc_secured_single_week.compute_factor(
        pd.Timestamp('2024-01-31', tz='UTC'),
        pd.Timestamp('2024-02-29', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.0796553173602354)
    assert str(factor) == "f = 4/52 + 1/366 = 0.07965532"
    assert factor.to_folded_string() == "f = 4/52 + 1/366 = 0.07965532"

def test_compute_factor_negative_period(dc_month):
    with pytest.raises(ValueError, match="end must be after start"):
        dc_month.compute_factor(
            pd.Timestamp('2025-02-01', tz='UTC'),
            pd.Timestamp('2025-01-01', tz='UTC')
        )

def test_months_between_dates(dc_month):
    # pylint: disable=W0212
    # Access to a protected member
    # Tests correction of wrong ordered dates
    months = dc_month._months_between_dates(
        pd.Timestamp('2025-02-01', tz='UTC'),
        pd.Timestamp('2025-01-01', tz='UTC')
    )
    assert months == 1

def test_default_instance():
    dc = UKConcApp()
    assert dc.is_secured_on_land is False
    assert dc.has_single_payment is False
    assert dc.time_period == DayCountTimePeriod.MONTH
    assert dc.day_count_origin == DayCountOrigin.DRAWDOWN
    assert dc.use_post_dates is True
    assert dc.include_non_financing_flows is True

def test_invalid_day_count_time_period():
    with pytest.raises(ValueError, match="Only month and week time periods are supported"):
        UKConcApp(time_period=DayCountTimePeriod.DAY)
