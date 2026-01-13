# tests/daycount/test_act_365.py
# pylint: disable=C0114, C0116, W0621
# - C0114: missing-module-docstring
# - C0116: missing-function-docstring
# - W0621: redefined-outer-name

import pytest
import pandas as pd
from curo.daycount.actual_365 import Actual365
from curo.enums import DayCountOrigin

@pytest.fixture
def dc():
    return Actual365()

def test_compute_factor_2020_01_28_to_2020_02_28(dc):
    factor = dc.compute_factor(
        pd.Timestamp('2020-01-28', tz='UTC'),
        pd.Timestamp('2020-02-28', tz='UTC')
    )
    assert factor.primary_period_fraction == 31 / 365
    assert str(factor) == "f = 31/365 = 0.08493151"
    assert factor.to_folded_string() == "f = 31/365 = 0.08493151"

def test_compute_factor_2019_01_28_to_2019_02_28(dc):
    factor = dc.compute_factor(
        pd.Timestamp('2019-01-28', tz='UTC'),
        pd.Timestamp('2019-02-28', tz='UTC')
    )
    assert factor.primary_period_fraction == 31 / 365
    assert str(factor) == "f = 31/365 = 0.08493151"
    assert factor.to_folded_string() == "f = 31/365 = 0.08493151"

def test_compute_factor_2017_12_31_to_2019_12_31(dc):
    factor = dc.compute_factor(
        pd.Timestamp('2017-12-31', tz='UTC'),
        pd.Timestamp('2019-12-31', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(730 / 365)
    assert str(factor) == "f = 730/365 = 2.00000000"
    assert factor.to_folded_string() == "f = 2 = 2.00000000"

def test_compute_factor_2018_12_31_to_2020_12_31(dc):
    factor = dc.compute_factor(
        pd.Timestamp('2018-12-31', tz='UTC'),
        pd.Timestamp('2020-12-31', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(731 / 365)
    assert str(factor) == "f = 731/365 = 2.00273973"
    assert factor.to_folded_string() == "f = 2 + 1/365 = 2.00273973"

def test_compute_factor_2019_06_30_to_2021_06_30(dc):
    factor = dc.compute_factor(
        pd.Timestamp('2019-06-30', tz='UTC'),
        pd.Timestamp('2021-06-30', tz='UTC')
    )
    assert factor.primary_period_fraction == pytest.approx(731 / 365)
    assert str(factor) == "f = 731/365 = 2.00273973"
    assert factor.to_folded_string() == "f = 2 + 1/365 = 2.00273973"

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

def test_default_instance():
    dc = Actual365()
    assert dc.day_count_origin == DayCountOrigin.NEIGHBOUR
    assert dc.use_post_dates is True
    assert dc.include_non_financing_flows is False

def test_use_xirr_method():
    dc = Actual365(use_xirr_method=True)
    assert dc.day_count_origin == DayCountOrigin.DRAWDOWN
