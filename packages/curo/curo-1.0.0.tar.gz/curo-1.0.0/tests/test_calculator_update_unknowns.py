# test_calculator_update_unknowns.py
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
from curo.enums import CashFlowColumn as Column, SortColumn
from curo.series import SeriesAdvance, SeriesPayment

@pytest.fixture
def calculator():
    from curo.calculator import Calculator
    return Calculator(precision=2)

start_date = pd.Timestamp("2022-01-01", tz="UTC")

def create_cash_flows(calculator, series_list, start_date):
    calculator._series = series_list
    cash_flows = calculator._build_profile(start_date)
    cash_flows = calculator._sort_cash_flows(cash_flows, sort_by=SortColumn.POST_DATE)
    # Ensure weighting column exists
    if Column.WEIGHTING.value not in cash_flows:
        cash_flows[Column.WEIGHTING.value] = 1.0
    return cash_flows

def test_update_unknowns_no_rounding(calculator):
    series = [
        SeriesAdvance(post_date_from=start_date, amount=-1000.0),
        SeriesPayment(post_date_from=start_date, amount=None),
        SeriesPayment(post_date_from=start_date, amount=None),
    ]
    cash_flows = create_cash_flows(calculator, series, start_date)

    result = calculator._update_unknowns(cash_flows, value=500.006, precision=2, is_rounded=False)

    assert result.loc[0, Column.AMOUNT.value] == -1000.0
    assert result.loc[1, Column.AMOUNT.value] == 500.006
    assert result.loc[2, Column.AMOUNT.value] == 500.006
    assert result.loc[1, Column.IS_KNOWN.value] == False
    assert result.loc[2, Column.IS_KNOWN.value] == False

def test_update_unknowns_rounding(calculator):
    series = [
        SeriesAdvance(post_date_from=start_date, amount=-1000.0),
        SeriesPayment(post_date_from=start_date, amount=None),
        SeriesPayment(post_date_from=start_date, amount=None),
    ]
    cash_flows = create_cash_flows(calculator, series, start_date)

    result = calculator._update_unknowns(cash_flows, value=500.006, precision=2, is_rounded=True)

    assert result.loc[0, Column.AMOUNT.value] == -1000.0
    assert result.loc[1, Column.AMOUNT.value] == 500.01
    assert result.loc[2, Column.AMOUNT.value] == 500.01
    assert result.loc[1, Column.IS_KNOWN.value] == False
    assert result.loc[2, Column.IS_KNOWN.value] == False

def test_update_unknowns_custom_weighting(calculator):
    series = [
        SeriesAdvance(post_date_from=start_date, amount=-1000.0),
        SeriesPayment(post_date_from=start_date, amount=None, weighting=2.0),
        SeriesPayment(post_date_from=start_date, amount=None, weighting=0.5),
    ]
    cash_flows = create_cash_flows(calculator, series, start_date)

    result = calculator._update_unknowns(cash_flows, value=500.006, precision=2, is_rounded=True)

    assert result.loc[0, Column.AMOUNT.value] == -1000.0
    assert result.loc[1, Column.AMOUNT.value] == 1000.01  # 500.006 * 2.0
    assert result.loc[2, Column.AMOUNT.value] == 250.00   # 500.006 * 0.5
    assert result.loc[1, Column.IS_KNOWN.value] == False
    assert result.loc[2, Column.IS_KNOWN.value] == False

def test_update_unknowns_no_unknowns(calculator):
    series = [
        SeriesAdvance(post_date_from=start_date, amount=-1000.0),
        SeriesPayment(post_date_from=start_date, amount=500.0),
    ]
    cash_flows = create_cash_flows(calculator, series, start_date)

    result = calculator._update_unknowns(cash_flows, value=500.006, precision=2, is_rounded=True)

    assert result.loc[0, Column.AMOUNT.value] == -1000.0
    assert result.loc[1, Column.AMOUNT.value] == 500.0
    assert result.loc[0, Column.IS_KNOWN.value] == True

def test_update_unknowns_zero_value(calculator):
    series = [
        SeriesAdvance(post_date_from=start_date, amount=-1000.0),
        SeriesPayment(post_date_from=start_date, amount=None, weighting=2.0),
    ]
    cash_flows = create_cash_flows(calculator, series, start_date)

    result = calculator._update_unknowns(cash_flows, value=0.0, precision=2, is_rounded=True)

    assert result.loc[0, Column.AMOUNT.value] == -1000.0
    assert result.loc[1, Column.AMOUNT.value] == 0.0
    assert result.loc[1, Column.IS_KNOWN.value] == False
