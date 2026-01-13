# tests/daycount/test_actual_isda.py
# pylint: disable=C0114, C0116, W0621
# - C0114: missing-module-docstring
# - C0116: missing-function-docstring
# - W0621: redefined-outer-name

import pytest
import pandas as pd
from curo.daycount.actual_isda import ActualISDA
from curo.enums import DayCountOrigin

@pytest.fixture
def dc():
    return ActualISDA()

def test_compute_factor_2020_01_28_to_2020_02_28(dc):
    factor = dc.compute_factor(
        pd.Timestamp('2020-01-28', tz='UTC'),
        pd.Timestamp('2020-02-28', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(31 / 366)
    assert str(factor) == "f = 31/366 = 0.08469945"
    assert factor.to_folded_string() == "f = 31/366 = 0.08469945"

def test_compute_factor_2019_01_28_to_2019_02_28(dc):
    factor = dc.compute_factor(
        pd.Timestamp('2019-01-28', tz='UTC'),
        pd.Timestamp('2019-02-28', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(31 / 365)
    assert str(factor) == "f = 31/365 = 0.08493151"
    assert factor.to_folded_string() == "f = 31/365 = 0.08493151"

def test_compute_factor_2017_12_31_to_2019_12_31(dc):
    factor = dc.compute_factor(
        pd.Timestamp('2017-12-31', tz='UTC'),
        pd.Timestamp('2019-12-31', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(1/365 + 365/365 + 364/365)
    assert str(factor) == "f = 1/365 + 365/365 + 364/365 = 2.00000000"
    assert factor.to_folded_string() == "f = 1/365 + 1 + 364/365 = 2.00000000"

def test_compute_factor_2018_12_31_to_2020_12_31(dc):
    factor = dc.compute_factor(
        pd.Timestamp('2018-12-31', tz='UTC'),
        pd.Timestamp('2020-12-31', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(1/365 + 365/365 + 365/366)
    assert str(factor) == "f = 1/365 + 365/365 + 365/366 = 2.00000749"
    assert factor.to_folded_string() == "f = 1/365 + 1 + 365/366 = 2.00000749"

def test_compute_factor_2019_06_30_to_2021_06_30(dc):
    factor = dc.compute_factor(
        pd.Timestamp('2019-06-30', tz='UTC'),
        pd.Timestamp('2021-06-30', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(185/365 + 366/366 + 180/365)
    assert str(factor) == "f = 185/365 + 366/366 + 180/365 = 2.00000000"
    assert factor.to_folded_string() == "f = 185/365 + 1 + 180/365 = 2.00000000"

def test_compute_factor_same_day(dc):
    factor = dc.compute_factor(
        pd.Timestamp('2020-01-01', tz='UTC'),
        pd.Timestamp('2020-01-01', tz='UTC')
    )
    assert factor.primary_period_fraction == 0
    assert str(factor) == "f = 0/365 = 0.00000000"
    assert factor.to_folded_string() == "f = 0 = 0.00000000"

def test_compute_factor_negative_period(dc):
    with pytest.raises(ValueError, match="end must be after start"):
        dc.compute_factor(
            pd.Timestamp('2020-02-01', tz='UTC'),
            pd.Timestamp('2020-01-01', tz='UTC')
        )

def test_compute_factor_year_end_to_year_end(dc):
    factor = dc.compute_factor(
        pd.Timestamp('2019-12-31', tz='UTC'),
        pd.Timestamp('2020-12-31', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(1/365 + 365/366)
    assert str(factor) == "f = 1/365 + 365/366 = 1.00000749"
    assert factor.to_folded_string() == "f = 1/365 + 365/366 = 1.00000749"

def test_compute_factor_leap_year_edge(dc):
    factor = dc.compute_factor(
        pd.Timestamp('2020-02-29', tz='UTC'),
        pd.Timestamp('2021-02-28', tz='UTC')
    )
    # 2020-02-29 -> 2020-12-31 = 307 days (inclusive)
    # 2021-01-01 -> 2021-02-28 = 58 days (excluding last day)
    assert factor.primary_period_fraction == pytest.approx(307/366 + 58/365)
    assert str(factor) == "f = 307/366 + 58/365 = 0.99770192"
    assert factor.to_folded_string() == "f = 307/366 + 58/365 = 0.99770192"

def test_compute_factor_cross_year_single_day(dc):
    factor = dc.compute_factor(
        pd.Timestamp('2019-12-31', tz='UTC'),
        pd.Timestamp('2020-01-01', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(1/365)
    assert str(factor) == "f = 1/365 = 0.00273973"
    assert factor.to_folded_string() == "f = 1/365 = 0.00273973"

def test_default_instance():
    dc = ActualISDA()
    assert dc.day_count_origin == DayCountOrigin.NEIGHBOUR
    assert dc.use_post_dates is True
    assert dc.include_non_financing_flows is False

def test_use_xirr_method():
    dc = ActualISDA(use_xirr_method=True)
    assert dc.day_count_origin == DayCountOrigin.DRAWDOWN
