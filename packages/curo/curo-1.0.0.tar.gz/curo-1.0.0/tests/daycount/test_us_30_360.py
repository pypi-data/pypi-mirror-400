# tests/daycount/test_us_30_360.py
# pylint: disable=C0114, C0116, W0621
# - C0114: missing-module-docstring
# - C0116: missing-function-docstring
# - W0621: redefined-outer-name

import pytest
import pandas as pd
from curo.daycount.us_30_360 import US30360
from curo.enums import DayCountOrigin

@pytest.fixture
def dc_default():
    return US30360()

@pytest.fixture
def dc_xirr():
    return US30360(use_xirr_method=True)

def test_compute_factor_2020_01_28_to_2020_02_29(dc_default):
    factor = dc_default.compute_factor(
        pd.Timestamp('2020-01-28', tz='UTC'),
        pd.Timestamp('2020-02-29', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.08611111111111111)
    assert str(factor) == "f = 31/360 = 0.08611111"
    assert factor.to_folded_string() == "f = 31/360 = 0.08611111"

def test_compute_factor_2019_01_28_to_2019_02_28(dc_default):
    factor = dc_default.compute_factor(
        pd.Timestamp('2019-01-28', tz='UTC'),
        pd.Timestamp('2019-02-28', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.08333333333333333)
    assert str(factor) == "f = 30/360 = 0.08333333"
    assert factor.to_folded_string() == "f = 30/360 = 0.08333333"

def test_compute_factor_2019_06_16_to_2019_07_31(dc_default):
    factor = dc_default.compute_factor(
        pd.Timestamp('2019-06-16', tz='UTC'),
        pd.Timestamp('2019-07-31', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(0.125)
    assert str(factor) == "f = 45/360 = 0.12500000"
    assert factor.to_folded_string() == "f = 45/360 = 0.12500000"

def test_compute_factor_2017_12_31_to_2019_12_31(dc_default):
    factor = dc_default.compute_factor(
        pd.Timestamp('2017-12-31', tz='UTC'),
        pd.Timestamp('2019-12-31', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(2.0)
    assert str(factor) == "f = 2 = 2.00000000"
    assert factor.to_folded_string() == "f = 2 = 2.00000000"

def test_compute_factor_2018_12_31_to_2020_12_31(dc_default):
    factor = dc_default.compute_factor(
        pd.Timestamp('2018-12-31', tz='UTC'),
        pd.Timestamp('2020-12-31', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(2.0)
    assert str(factor) == "f = 2 = 2.00000000"
    assert factor.to_folded_string() == "f = 2 = 2.00000000"

def test_compute_factor_2019_06_30_to_2021_06_30(dc_default):
    factor = dc_default.compute_factor(
        pd.Timestamp('2019-06-30', tz='UTC'),
        pd.Timestamp('2021-06-30', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(2.0)
    assert str(factor) == "f = 2 = 2.00000000"
    assert factor.to_folded_string() == "f = 2 = 2.00000000"

def test_compute_factor_negative_period(dc_default):
    with pytest.raises(ValueError, match="end must be after start"):
        dc_default.compute_factor(
            pd.Timestamp('2020-02-01', tz='UTC'),
            pd.Timestamp('2020-01-01', tz='UTC')
        )

def test_compute_factor_same_day(dc_default):
    factor = dc_default.compute_factor(
        pd.Timestamp('2020-01-01', tz='UTC'),
        pd.Timestamp('2020-01-01', tz='UTC')
    )
    assert factor.primary_period_fraction == 0.0
    assert str(factor) == "f = 0 = 0.00000000"
    assert factor.to_folded_string() == "f = 0 = 0.00000000"

def test_default_instance(dc_default):
    assert dc_default.day_count_origin == DayCountOrigin.NEIGHBOUR
    assert dc_default.use_post_dates is True
    assert dc_default.include_non_financing_flows is False

def test_xirr_instance(dc_xirr):
    assert dc_xirr.day_count_origin == DayCountOrigin.DRAWDOWN
    assert dc_xirr.use_post_dates is True
    assert dc_xirr.include_non_financing_flows is False
