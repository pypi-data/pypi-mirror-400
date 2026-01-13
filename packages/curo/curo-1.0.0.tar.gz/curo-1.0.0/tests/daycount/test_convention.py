# tests/daycount/test_convention.py
# pylint: disable=C0114, C0116, W0621
# - C0114: missing-module-docstring
# - C0116: missing-function-docstring
# - W0621: redefined-outer-name

import pytest
import pandas as pd
from curo.daycount.convention import Convention
from curo.enums import DayCountOrigin

def test_convention_init_defaults():
    convention = Convention()
    assert convention.use_post_dates is False
    assert convention.include_non_financing_flows is False
    assert convention.use_xirr_method is False

def test_convention_init_custom():
    convention = Convention(
        use_post_dates=True,
        include_non_financing_flows=True,
        use_xirr_method=True
    )
    assert convention.use_post_dates is True
    assert convention.include_non_financing_flows is True
    assert convention.use_xirr_method is True

def test_day_count_origin_drawdown():
    convention = Convention(use_xirr_method=True)
    assert convention.day_count_origin == DayCountOrigin.DRAWDOWN

def test_day_count_origin_neighbour():
    convention = Convention(use_xirr_method=False)
    assert convention.day_count_origin == DayCountOrigin.NEIGHBOUR

def test_compute_factor_not_implemented():
    convention = Convention()
    with pytest.raises(NotImplementedError):
        convention.compute_factor(
            start=pd.Timestamp('2025-01-01', tz='UTC'),
            end=pd.Timestamp('2025-02-01', tz='UTC')
        )
