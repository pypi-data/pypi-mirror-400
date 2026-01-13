# test_calculator_solve_rate.py
# pylint: disable=C0114,C0116,C0121,C0415,W0212,W0621 #C0121
# - C0114: missing-module-docstring
# - C0115: missing-class-docstring
# - C0116: missing-function-docstring
# - C0121: singleton-comparison
# - C0415: import-outside-toplevel
# - W0212: protected-access
# - W0621: redefined-outer-name

import pytest
import pandas as pd
from curo.daycount.us_30_360 import US30360
from curo.daycount.us_appendix_j import USAppendixJ
from curo.enums import CashFlowColumn as Column
from curo.exceptions import UnsolvableError, ValidationError
from curo.series import SeriesAdvance, SeriesCharge, SeriesPayment

@pytest.fixture
def calculator():
    from curo.calculator import Calculator
    return Calculator(precision=2)

start_date = pd.Timestamp("2022-01-01", tz="UTC")
date2 = pd.Timestamp("2022-02-01", tz="UTC")
date3 = pd.Timestamp("2022-03-01", tz="UTC")
date4 = pd.Timestamp("2022-04-01", tz="UTC")

def create_bespoke_profile():
    return pd.DataFrame({
        Column.AMOUNT.value: [-1000.0, 10.0, 340.02, 340.02, 340.02],
        Column.POST_DATE.value: [start_date, start_date, date2, date3, date4],
        Column.IS_CHARGE.value: [False, True, False, False, False],
        Column.IS_INTEREST_CAPITALISED.value: [None, None, True, True, True],
        Column.IS_KNOWN.value: [True, True, True, True, True],
        Column.MODE.value: ["advance", "charge", "payment", "payment", "payment"],
        Column.LABEL.value: ["Advance", "Charge", "Payment 1", "Payment 2", "Payment 3"],
        Column.VALUE_DATE.value: [start_date, start_date, date2, date3, date4],
        Column.WEIGHTING.value: [1.0, 1.0, 1.0, 1.0, 1.0]
    })

def test_solve_rate_regular_drawdown_1971_percent(calculator):
    # Regular Drawdown (19.71%, US30360):
    convention = US30360(include_non_financing_flows=True, use_xirr_method=True)
    calculator._series = [
        SeriesAdvance(post_date_from=start_date, amount=-1000.0),
        SeriesCharge(post_date_from=start_date, amount=10.0),
        SeriesPayment(post_date_from=date2, amount=340.02),
        SeriesPayment(post_date_from=date3, amount=340.02),
        SeriesPayment(post_date_from=date4, amount=340.02),
    ]
    calculator._is_bespoke_profile = False
    rate = calculator.solve_rate(convention, upper_bound=10.0)
    assert abs(rate - 0.19712195000183072) < 1e-8

def test_solve_rate_usappendixj_annualization(calculator):
    # USAppendixJ Annualization
    convention = USAppendixJ()  # periods_in_year = 12
    calculator._series = [
        SeriesAdvance(post_date_from=start_date, amount=-1000.0),
        SeriesPayment(post_date_from=date2, amount=340.02),
        SeriesPayment(post_date_from=date3, amount=340.02),
        SeriesPayment(post_date_from=date4, amount=340.02),
    ]
    calculator._is_bespoke_profile = False
    rate = calculator.solve_rate(convention, upper_bound=10.0)
    assert abs(rate - 0.11996224313275361) < 1e-8

def test_solve_rate_bespoke_profile(calculator):
    convention = US30360(include_non_financing_flows=True, use_xirr_method=True)
    calculator.profile = create_bespoke_profile()
    calculator._is_bespoke_profile = True
    calculator._series = []  # Empty series
    rate = calculator.solve_rate(convention, upper_bound=10.0)
    assert abs(rate - 0.19712195000183072) < 1e-8

def test_solve_rate_invalid_bespoke_profile(calculator):
    convention = US30360()
    calculator._profile = None
    calculator._is_bespoke_profile = True
    with pytest.raises(ValidationError, match="Bespoke profile must be a non-empty DataFrame"):
        calculator.solve_rate(convention, upper_bound=10.0)

def test_solve_rate_empty_series(calculator):
    convention = US30360()
    calculator._series = []
    calculator._is_bespoke_profile = False
    with pytest.raises(ValidationError, match="No cash flow series provided"):
        calculator.solve_rate(convention, upper_bound=10.0)

def test_solve_rate_invalid_upper_bound(calculator):
    convention = US30360()
    calculator._series = [
        SeriesAdvance(post_date_from=start_date, amount=-1000.0),
        SeriesPayment(post_date_from=date2, amount=340.02),
    ]
    calculator._is_bespoke_profile = False
    with pytest.raises(ValidationError, match="Upper bound must be positive"):
        calculator.solve_rate(convention, upper_bound=0.0)

def test_solve_rate_empty_profile(calculator):
    with pytest.raises(ValidationError, match="No cash flow series provided"):
        calculator.solve_rate(convention=USAppendixJ())

def test_solve_rate_no_solution(calculator):
    convention = US30360()
    calculator._series = [
        SeriesAdvance(post_date_from=start_date, amount=-1000.0),
        SeriesPayment(post_date_from=date2, amount=0.01),
    ]
    calculator._is_bespoke_profile = False
    with pytest.raises(UnsolvableError, match="No interest rate found"):
        calculator.solve_rate(convention, upper_bound=10.0)
