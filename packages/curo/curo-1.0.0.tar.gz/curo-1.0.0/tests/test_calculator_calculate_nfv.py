# test_calculator_calculate_nfv.py
# pylint: disable=C0114,C0116,C0415,W0212,W0621 #C0121
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
from curo.enums import CashFlowColumn as Column, SortColumn
from curo.series import SeriesAdvance, SeriesPayment, SeriesCharge

@pytest.fixture
def calculator():
    from curo.calculator import Calculator
    return Calculator(precision=2)

def create_cash_flows(calculator, series_list, start_date):
    calculator._series = series_list
    cash_flows = calculator._build_profile(start_date)
    return calculator._sort_cash_flows(cash_flows, sort_by=SortColumn.POST_DATE)

start_date = pd.Timestamp("2022-01-01", tz="UTC")
date2 = pd.Timestamp("2022-02-01", tz="UTC")
date3 = pd.Timestamp("2022-03-01", tz="UTC")
date4 = pd.Timestamp("2022-04-01", tz="UTC")

def test_calculate_nfv_regular_neighbour_12_percent(calculator):
    # Regular Compounding, NEIGHBOUR (12%), exclude charges
    convention = US30360()
    series = [
        SeriesAdvance(post_date_from=start_date, amount=-1000.0),
        SeriesPayment(post_date_from=date2, amount=340.02),
        SeriesPayment(post_date_from=date3, amount=340.02),
        SeriesPayment(post_date_from=date4, amount=340.02),
        SeriesCharge(post_date_from=start_date, amount=10.0),
    ]
    cash_flows = create_cash_flows(calculator, series, start_date)
    cash_flows = calculator._assign_factors(cash_flows, convention)

    nfv = calculator._calculate_nfv(cash_flows, convention, 0.12)
    assert abs(nfv - (-0.006398)) < 1e-8

def test_calculate_nfv_irregular_neighbour_1216_percent(calculator):
    # Irregular Compounding, NEIGHBOUR (12.16%), exclude charges
    convention = US30360()
    series = [
        SeriesAdvance(post_date_from=start_date, amount=-1000.0),
        SeriesPayment(post_date_from=date2, amount=340.02, is_interest_capitalised=False),
        SeriesPayment(post_date_from=date3, amount=340.02, is_interest_capitalised=False),
        SeriesPayment(post_date_from=date4, amount=340.02),
        SeriesCharge(post_date_from=start_date, amount=10.0),
    ]
    cash_flows = create_cash_flows(calculator, series, start_date)
    cash_flows = calculator._assign_factors(cash_flows, convention)

    nfv = calculator._calculate_nfv(cash_flows, convention, 0.1216)
    assert abs(nfv - (-0.003392)) < 1e-8

def test_calculate_nfv_regular_drawdown_1971_percent(calculator):
    # Regular Compounding, DRAWDOWN (19.71%, XIRR)
    convention = US30360(include_non_financing_flows=True, use_xirr_method=True)
    series = [
        SeriesAdvance(post_date_from=start_date, amount=-1000.0),
        SeriesPayment(post_date_from=date2, amount=340.02),
        SeriesPayment(post_date_from=date3, amount=340.02),
        SeriesPayment(post_date_from=date4, amount=340.02),
        SeriesCharge(post_date_from=start_date, amount=10.0),
    ]
    cash_flows = create_cash_flows(calculator, series, start_date)
    cash_flows = calculator._assign_factors(cash_flows, convention)

    nfv = calculator._calculate_nfv(cash_flows, convention, 0.1971)
    assert abs(nfv - 0.003011) < 1e-6

def test_calculate_nfv_irregular_drawdown_1268_percent(calculator):
    # Irregular Compounding, DRAWDOWN (12.68%, XIRR)
    convention = US30360(include_non_financing_flows=False, use_xirr_method=True)
    series = [
        SeriesAdvance(post_date_from=start_date, amount=-1000.0),
        SeriesPayment(post_date_from=date2, amount=340.02, is_interest_capitalised=False),
        SeriesPayment(post_date_from=date3, amount=340.02, is_interest_capitalised=False),
        SeriesPayment(post_date_from=date4, amount=340.02),
        SeriesCharge(post_date_from=start_date, amount=10.0),
    ]
    cash_flows = create_cash_flows(calculator, series, start_date)
    cash_flows = calculator._assign_factors(cash_flows, convention)

    nfv = calculator._calculate_nfv(cash_flows, convention, 0.1268)
    assert abs(nfv - (-0.002520)) < 1e-6

def test_calculate_nfv_single_cash_flow(calculator):
    # Edge Case: Single Cash Flow (expecting NFV = amount)
    convention = US30360()
    series = [SeriesAdvance(post_date_from=start_date, amount=-1000.0)]
    cash_flows = create_cash_flows(calculator, series, start_date)
    cash_flows = calculator._assign_factors(cash_flows, convention)

    nfv = calculator._calculate_nfv(cash_flows, convention, 0.12)
    assert abs(nfv - (-1000.0)) < 1e-8

def test_calculate_nfv_no_cash_flows(calculator):
    # Edge Case: No Advances
    # [should raise ValidationError in _assign_factors, but test NFV with empty cash flows]
    convention = US30360()
    cash_flows = pd.DataFrame(columns=[col.value for col in Column] + ['factor'])
    nfv = calculator._calculate_nfv(cash_flows, convention, 0.12)
    assert nfv == 0.0

def test_calculate_nfv_usappendixj_drawdown(calculator):
    # pylint: disable=C0301:line-too-long
    # Test USAppendixJ with DRAWDOWN, covering all conditionals
    convention = USAppendixJ()
    series = [
        SeriesAdvance(post_date_from=start_date, amount=-1000.0),  # 2022-01-01
        SeriesPayment(post_date_from=date2, amount=340.02),  # 2022-02-01 (full month)
        SeriesPayment(post_date_from=pd.Timestamp("2022-02-16", tz="UTC"), amount=340.02),  # Partial period
        SeriesPayment(post_date_from=date3, amount=340.02),  # 2022-03-01
        SeriesCharge(post_date_from=start_date, amount=10.0),  # 2022-01-01
    ]
    cash_flows = create_cash_flows(calculator, series, start_date)
    cash_flows = calculator._assign_factors(cash_flows, convention)

    # The annual interest rate that yields NFV ~0.00 is 0.2418315 (verified with Dart library)
    # The rate guess passed to solve _calculate_nfv for USAppendixJ is the *periodic* rate
    # which in example is the annual rate / 12 months in a year
    nfv = calculator._calculate_nfv(cash_flows, convention, (0.2418315/12))
    assert abs(nfv) < 0.000001
