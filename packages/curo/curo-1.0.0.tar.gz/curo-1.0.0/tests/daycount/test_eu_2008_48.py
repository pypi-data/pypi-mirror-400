# tests/daycount/test_eu_2008_48_ec.py
# pylint: disable=C0114, C0116, W0621
# - C0114: missing-module-docstring
# - C0116: missing-function-docstring
# - W0621: redefined-outer-name

import pytest
import pandas as pd
from curo.daycount.eu_2008_48 import EU200848EC
from curo.enums import DayCountOrigin, DayCountTimePeriod

@pytest.fixture
def dc_year():
    return EU200848EC(time_period=DayCountTimePeriod.YEAR)

@pytest.fixture
def dc_month():
    return EU200848EC(time_period=DayCountTimePeriod.MONTH)

@pytest.fixture
def dc_week():
    return EU200848EC(time_period=DayCountTimePeriod.WEEK)

def test_compute_factor_year_time_period(dc_year):
    assert dc_year.time_period == DayCountTimePeriod.YEAR

def test_compute_factor_year_2019_01_12_to_2020_01_12(dc_year):
    factor = dc_year.compute_factor(
        pd.Timestamp('2019-01-12', tz='UTC'),
        pd.Timestamp('2020-01-12', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(1.0)
    assert str(factor) == "f = 1 = 1.00000000"
    assert factor.to_folded_string() == "f = 1 = 1.00000000"

def test_compute_factor_year_2012_01_12_to_2012_02_15(dc_year):
    factor = dc_year.compute_factor(
        pd.Timestamp('2012-01-12', tz='UTC'),
        pd.Timestamp('2012-02-15', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.0931506849315069)
    assert str(factor) == "f = 34/365 = 0.09315068"
    assert factor.to_folded_string() == "f = 34/365 = 0.09315068"

def test_compute_factor_year_2019_02_28_to_2020_02_29(dc_year):
    factor = dc_year.compute_factor(
        pd.Timestamp('2019-02-28', tz='UTC'),
        pd.Timestamp('2020-02-29', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(1.0)
    assert str(factor) == "f = 1 = 1.00000000"
    assert factor.to_folded_string() == "f = 1 = 1.00000000"

def test_compute_factor_year_2020_02_28_to_2021_02_28(dc_year):
    factor = dc_year.compute_factor(
        pd.Timestamp('2020-02-28', tz='UTC'),
        pd.Timestamp('2021-02-28', tz='UTC')
    )
    # Need to determine from regs if a year time interval which spans
    # a leap-day is counted as exactly 1 year, or should be 1 year + 1 day.
    # If the latter, compute_factor will need to be updated to use EOM processing
    # i.e. similar to the implementation used in us_appendix_j
    assert factor.primary_period_fraction == pytest.approx(1.0)
    assert str(factor) == "f = 1 = 1.00000000"
    assert factor.to_folded_string() == "f = 1 = 1.00000000"

def test_compute_factor_year_2020_02_29_to_2021_02_28(dc_year):
    factor = dc_year.compute_factor(
        pd.Timestamp('2020-02-29', tz='UTC'),
        pd.Timestamp('2021-02-28', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(1.0)
    assert str(factor) == "f = 1 = 1.00000000"
    assert factor.to_folded_string() == "f = 1 = 1.00000000"

def test_compute_factor_month_time_period(dc_month):
    assert dc_month.time_period == DayCountTimePeriod.MONTH

def test_compute_factor_month_2019_01_12_to_2020_01_12(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2019-01-12', tz='UTC'),
        pd.Timestamp('2020-01-12', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(1.0)
    assert str(factor) == "f = 1 = 1.00000000"
    assert factor.to_folded_string() == "f = 1 = 1.00000000"

def test_compute_factor_month_2012_01_12_to_2012_02_15(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2012-01-12', tz='UTC'),
        pd.Timestamp('2012-02-15', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.0915525114155251)
    assert str(factor) == "f = 1/12 + 3/365 = 0.09155251"
    assert factor.to_folded_string() == "f = 1/12 + 3/365 = 0.09155251"

def test_compute_factor_month_2012_01_12_to_2012_03_15(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2012-01-12', tz='UTC'),
        pd.Timestamp('2012-03-15', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.17488584474885843)
    assert str(factor) == "f = 2/12 + 3/365 = 0.17488584"
    assert factor.to_folded_string() == "f = 2/12 + 3/365 = 0.17488584"

def test_compute_factor_month_2012_01_12_to_2012_04_15(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2012-01-12', tz='UTC'),
        pd.Timestamp('2012-04-15', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.2582191780821918)
    assert str(factor) == "f = 3/12 + 3/365 = 0.25821918"
    assert factor.to_folded_string() == "f = 3/12 + 3/365 = 0.25821918"

def test_compute_factor_month_2013_01_12_to_2013_02_15(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2013-01-12', tz='UTC'),
        pd.Timestamp('2013-02-15', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.09153005464480873)
    assert str(factor) == "f = 1/12 + 3/366 = 0.09153005"
    assert factor.to_folded_string() == "f = 1/12 + 3/366 = 0.09153005"

def test_compute_factor_month_2013_01_12_to_2013_03_15(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2013-01-12', tz='UTC'),
        pd.Timestamp('2013-03-15', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.17486338797814208)
    assert str(factor) == "f = 2/12 + 3/366 = 0.17486339"
    assert factor.to_folded_string() == "f = 2/12 + 3/366 = 0.17486339"

def test_compute_factor_month_2013_01_12_to_2013_04_15(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2013-01-12', tz='UTC'),
        pd.Timestamp('2013-04-15', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.2581967213114754)
    assert str(factor) == "f = 3/12 + 3/366 = 0.25819672"
    assert factor.to_folded_string() == "f = 3/12 + 3/366 = 0.25819672"

def test_compute_factor_month_2013_02_25_to_2013_03_28(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2013-02-25', tz='UTC'),
        pd.Timestamp('2013-03-28', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.09153005464480873)
    assert str(factor) == "f = 1/12 + 3/366 = 0.09153005"
    assert factor.to_folded_string() == "f = 1/12 + 3/366 = 0.09153005"

def test_compute_factor_month_2013_02_26_to_2013_03_29(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2013-02-26', tz='UTC'),
        pd.Timestamp('2013-03-29', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.08879781420765027)
    assert str(factor) == "f = 1/12 + 2/366 = 0.08879781"
    assert factor.to_folded_string() == "f = 1/12 + 2/366 = 0.08879781"

def test_compute_factor_month_2012_02_26_to_2012_03_29(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2012-02-26', tz='UTC'),
        pd.Timestamp('2012-03-29', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.09153005464480873)
    assert str(factor) == "f = 1/12 + 3/366 = 0.09153005"
    assert factor.to_folded_string() == "f = 1/12 + 3/366 = 0.09153005"

def test_compute_factor_month_2012_02_26_to_2012_02_26(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2012-02-26', tz='UTC'),
        pd.Timestamp('2012-02-26', tz='UTC')
    )
    assert factor.primary_period_fraction == 0.0
    assert str(factor) == "f = 0 = 0.00000000"
    assert factor.to_folded_string() == "f = 0 = 0.00000000"

def test_compute_factor_month_2025_01_30_to_2025_01_30(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2025-01-30', tz='UTC'),
        pd.Timestamp('2025-01-30', tz='UTC')
    )
    assert factor.primary_period_fraction == 0.0
    assert str(factor) == "f = 0 = 0.00000000"
    assert factor.to_folded_string() == "f = 0 = 0.00000000"

def test_compute_factor_month_2024_12_31_to_2025_02_28(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2024-12-31', tz='UTC'),
        pd.Timestamp('2025-02-28', tz='UTC')
    )
    # Both month-end dates so:
    # 2025-01-31 <- 2025-02-28 = 1
    # 2024-12-31 <- 2025-01-31 = 1
    # Factor = 2/12
    assert factor.primary_period_fraction == pytest.approx(0.16666666666666667)
    assert str(factor) == "f = 2/12 = 0.16666667"
    assert factor.to_folded_string() == "f = 2/12 = 0.16666667"

def test_compute_factor_month_2024_02_29_to_2025_03_31(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2024-02-29', tz='UTC'),
        pd.Timestamp('2025-03-31', tz='UTC')
    )
    # Both month-end dates so:
    # 2024-03-31 <- 2025-03-31 = 12 months or 1 year
    # 2024-02-29 <- 2024-03-31 = 1
    # Factor = 1 + 1/12
    assert factor.primary_period_fraction == pytest.approx(1.0833333333333333)
    assert str(factor) == "f = 1 + 1/12 = 1.08333333"
    assert factor.to_folded_string() == "f = 1 + 1/12 = 1.08333333"

def test_compute_factor_month_2024_02_28_to_2025_02_27(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2024-02-28', tz='UTC'),
        pd.Timestamp('2025-02-27', tz='UTC')
    )
     # Not month-end dates so:
    # 2024-03-27 <- 2025-02-27 = 11 months
    # 2024-02-28 <- 2024-03-27 = 28 days
    # Factor = 11/12 + 28/366
    assert factor.primary_period_fraction == pytest.approx(0.9931693989071040)
    assert str(factor) == "f = 11/12 + 28/366 = 0.99316940"
    assert factor.to_folded_string() == "f = 11/12 + 28/366 = 0.99316940"

def test_compute_factor_month_2024_02_28_to_2025_02_28(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2024-02-28', tz='UTC'),
        pd.Timestamp('2025-02-28', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(1.0)
    assert str(factor) == "f = 1 = 1.00000000"
    assert factor.to_folded_string() == "f = 1 = 1.00000000"

def test_compute_factor_month_2024_02_29_to_2025_02_28(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2024-02-29', tz='UTC'),
        pd.Timestamp('2025-02-28', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(1.0)
    assert str(factor) == "f = 1 = 1.00000000"
    assert factor.to_folded_string() == "f = 1 = 1.00000000"

def test_compute_factor_month_2023_02_28_to_2024_02_28(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2023-02-28', tz='UTC'),
        pd.Timestamp('2024-02-28', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(1.0)
    assert str(factor) == "f = 1 = 1.00000000"
    assert factor.to_folded_string() == "f = 1 = 1.00000000"

def test_compute_factor_month_2023_02_28_to_2024_02_29(dc_month):
    factor = dc_month.compute_factor(
        pd.Timestamp('2023-02-28', tz='UTC'),
        pd.Timestamp('2024-02-29', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(1.0)
    assert str(factor) == "f = 1 = 1.00000000"
    assert factor.to_folded_string() == "f = 1 = 1.00000000"

def test_compute_factor_negative_period_month(dc_month):
    with pytest.raises(ValueError, match="end must be after start"):
        dc_month.compute_factor(
            pd.Timestamp('2020-02-01', tz='UTC'),
            pd.Timestamp('2020-01-01', tz='UTC')
        )

def test_compute_factor_week_time_period(dc_week):
    assert dc_week.time_period == DayCountTimePeriod.WEEK

def test_compute_factor_week_2012_01_12_to_2012_01_26(dc_week):
    factor = dc_week.compute_factor(
        pd.Timestamp('2012-01-12', tz='UTC'),
        pd.Timestamp('2012-01-26', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.038461538461538464)
    assert str(factor) == "f = 2/52 = 0.03846154"
    assert factor.to_folded_string() == "f = 2/52 = 0.03846154"

def test_compute_factor_week_2012_01_12_to_2013_01_10(dc_week):
    factor = dc_week.compute_factor(
        pd.Timestamp('2012-01-12', tz='UTC'),
        pd.Timestamp('2013-01-10', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(1.0)
    assert str(factor) == "f = 1 = 1.00000000"
    assert factor.to_folded_string() == "f = 1 = 1.00000000"

def test_compute_factor_week_2012_01_12_to_2012_01_30(dc_week):
    factor = dc_week.compute_factor(
        pd.Timestamp('2012-01-12', tz='UTC'),
        pd.Timestamp('2012-01-30', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.0494204425711275)
    assert str(factor) == "f = 2/52 + 4/365 = 0.04942044"
    assert factor.to_folded_string() == "f = 2/52 + 4/365 = 0.04942044"

def test_compute_factor_week_2012_01_12_to_2013_01_12(dc_week):
    factor = dc_week.compute_factor(
        pd.Timestamp('2012-01-12', tz='UTC'),
        pd.Timestamp('2013-01-12', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(1.0054794520547945)
    assert str(factor) == "f = 1 + 2/365 = 1.00547945"
    assert factor.to_folded_string() == "f = 1 + 2/365 = 1.00547945"

def test_compute_factor_week_2012_01_12_to_2012_01_12(dc_week):
    factor = dc_week.compute_factor(
        pd.Timestamp('2012-01-12', tz='UTC'),
        pd.Timestamp('2012-01-12', tz='UTC')
    )
    assert factor.primary_period_fraction == 0.0
    assert str(factor) == "f = 0 = 0.00000000"
    assert factor.to_folded_string() == "f = 0 = 0.00000000"

def test_compute_factor_negative_period_week(dc_week):
    with pytest.raises(ValueError, match="end must be after start"):
        dc_week.compute_factor(
            pd.Timestamp('2020-02-01', tz='UTC'),
            pd.Timestamp('2020-01-01', tz='UTC')
        )

def test_default_instance():
    dc = EU200848EC()
    assert dc.time_period == DayCountTimePeriod.MONTH
    assert dc.day_count_origin == DayCountOrigin.DRAWDOWN
    assert dc.use_post_dates is True
    assert dc.include_non_financing_flows is True

def test_invalid_day_count_time_period():
    with pytest.raises(ValueError, match="Only year, month, and week time periods are supported"):
        EU200848EC(time_period=DayCountTimePeriod.DAY)
