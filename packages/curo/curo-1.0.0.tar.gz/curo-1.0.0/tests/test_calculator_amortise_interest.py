# test_calculator_amortise_interest.py
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
import numpy as np
from curo.daycount.us_30_360 import US30360
from curo.enums import CashFlowColumn as Column, SortColumn
from curo.series import SeriesAdvance, SeriesCharge, SeriesPayment

@pytest.fixture
def calculator():
    from curo.calculator import Calculator
    return Calculator(precision=2)

def create_cash_flows(calculator, series_list, start_date):
    calculator._series = series_list
    cash_flows = calculator._build_profile(start_date)
    return calculator._sort_cash_flows(cash_flows, sort_by=SortColumn.POST_DATE)

start_date = pd.Timestamp("2019-01-01", tz="UTC")
date2 = pd.Timestamp("2019-02-01", tz="UTC")
date3 = pd.Timestamp("2019-03-01", tz="UTC")
date4 = pd.Timestamp("2019-04-01", tz="UTC")

def test_amortise_interest_main(calculator):
    convention = US30360()  # NEIGHBOUR
    series = [
        SeriesAdvance(post_date_from=start_date, amount=-1000.0),
        SeriesCharge(post_date_from=start_date, amount=10.0),
        SeriesPayment(post_date_from=date2, amount=340.02, is_interest_capitalised=False),
        SeriesPayment(post_date_from=date3, amount=340.02, is_interest_capitalised=False),
        SeriesPayment(post_date_from=date4, amount=340.02),
    ]
    cash_flows = create_cash_flows(calculator, series, start_date)
    cash_flows = calculator._assign_factors(cash_flows, convention)

    result = calculator._amortise_interest(cash_flows, interest_rate=0.12, precision=2)

    assert result['interest'].dtype == np.float64
    assert result.loc[0, 'interest'] == 0.0  # Advance
    assert result.loc[1, 'interest'] == 0.0  # Charge
    assert result.loc[2, 'interest'] == 0.0  # Payment 1
    assert result.loc[3, 'interest'] == 0.0  # Payment 2
    assert abs(result.loc[4, 'interest'] - (-20.06)) < 1e-6  # Payment 3 (rounding adjustment)
    # Verify capital = amount - interest for last payment
    assert abs((result.loc[4, Column.AMOUNT.value] - result.loc[4, 'interest']) - 360.08) < 1e-6

def test_amortise_interest_all_capitalised(calculator):
    convention = US30360()
    series = [
        SeriesAdvance(post_date_from=start_date, amount=-1000.0),
        SeriesPayment(post_date_from=date2, amount=340.02, is_interest_capitalised=True),
        SeriesPayment(post_date_from=date3, amount=340.02, is_interest_capitalised=True),
    ]
    cash_flows = create_cash_flows(calculator, series, start_date)
    cash_flows = calculator._assign_factors(cash_flows, convention)

    result = calculator._amortise_interest(cash_flows, interest_rate=0.12, precision=2)

    assert result['interest'].dtype == np.float64
    assert result.loc[0, 'interest'] == 0.0
    assert abs(result.loc[1, 'interest'] - (-10.0)) < 1e-6  # Negative interest
    assert abs(result.loc[2, 'interest'] - 329.96) < 1e-6   # Final adjustment
    assert abs((result.loc[2, Column.AMOUNT.value] - result.loc[2, 'interest']) - 10.06) < 1e-6

def test_amortise_interest_no_payments(calculator):
    convention = US30360()
    series = [
        SeriesAdvance(post_date_from=start_date, amount=-1000.0),
        SeriesCharge(post_date_from=start_date, amount=10.0),
    ]
    cash_flows = create_cash_flows(calculator, series, start_date)
    cash_flows = calculator._assign_factors(cash_flows, convention)

    result = calculator._amortise_interest(cash_flows, interest_rate=0.12, precision=2)

    assert result['interest'].dtype == np.float64
    assert result.loc[0, 'interest'] == 0.0
    assert result.loc[1, 'interest'] == 0.0
