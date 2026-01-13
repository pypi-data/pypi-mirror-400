# test_calculator_assign_factors.py
# pylint: disable=C0114,C0116,C0415,W0212,W0621 #C0121
# - C0114: missing-module-docstring
# - C0115:missing-class-docstring
# - C0116: missing-function-docstring
# - C0121: singleton-comparison
# - C0415:import-outside-toplevel
# - W0212: protected-access
# - W0621: redefined-outer-name

import pytest
import pandas as pd
from curo.daycount.convention import Convention
from curo.daycount.day_count_factor import DayCountFactor
from curo.daycount.us_30_360 import US30360
from curo.enums import SortColumn
from curo.exceptions import ValidationError
from curo.series import SeriesAdvance, SeriesPayment, SeriesCharge
from curo.utils import gauss_round

class MockConvention(Convention):
    """
    Mock Convention for testing
    """
    def __init__(self,
                 use_post_dates=False,
                 include_non_financing_flows=False,
                 use_xirr_method=False):
        super().__init__(use_post_dates, include_non_financing_flows, use_xirr_method)
        self._calls = []  # Track compute_factor calls

    def compute_factor(self, start: pd.Timestamp, end: pd.Timestamp) -> DayCountFactor:
        days = (end - start).days
        factor = DayCountFactor(
            primary_period_fraction = days / 365.0,
            discount_factor_log = [f"{days}/365 = {gauss_round(days/365.0, 8):.8f}"],
        )
        self._calls.append((start, end, factor))
        return factor

# Fixture for Calculator
@pytest.fixture
def calculator():
    from curo.calculator import Calculator
    return Calculator(precision=2)

# Helper to create a cash flow DataFrame
def create_cash_flows(calculator, series_list, start_date):
    calculator._series = series_list
    return calculator._build_profile(start_date)

# Common dates
start_date = pd.Timestamp("2026-01-01", tz="UTC")
date2 = pd.Timestamp("2026-02-01", tz="UTC")
date3 = pd.Timestamp("2026-03-01", tz="UTC")

def test_assign_factors_drawdown_post_dates(calculator):
    # Test DRAWDOWN Origin with Post Dates
    convention = MockConvention(use_post_dates=True, use_xirr_method=True)
    advance = SeriesAdvance(post_date_from=start_date, amount=1000.0)
    payment = SeriesPayment(post_date_from=date2, amount=1050.0)
    cash_flows = create_cash_flows(calculator, [advance, payment], start_date)
    cash_flows = calculator._sort_cash_flows(cash_flows, sort_by=SortColumn.POST_DATE)

    result = calculator._assign_factors(cash_flows, convention)

    assert result['factor'].notna().all()
    assert len(convention._calls) == 2
    assert convention._calls[0][0] == start_date  # Advance: start to start
    assert convention._calls[0][1] == start_date
    assert convention._calls[1][0] == start_date  # Payment: start to date2
    assert convention._calls[1][1] == date2
    assert result.loc[0, 'factor'].primary_period_fraction == 0.0
    assert abs(result.loc[1, 'factor'].primary_period_fraction - 31/365.0) < 1e-8

def test_assign_factors_neighbour_value_dates(calculator):
    # Test NEIGHBOUR Origin with Value Dates
    # pylint: disable=C0301
    convention = MockConvention(use_post_dates=False, use_xirr_method=False)
    advance = SeriesAdvance(
        post_date_from=start_date,
        value_date_from=start_date + pd.Timedelta(days=1),
        amount=1000.0)
    payment = SeriesPayment(post_date_from=date2, amount=1050.0)  # value_date = post_date
    cash_flows = create_cash_flows(calculator, [advance, payment], start_date)
    cash_flows = calculator._sort_cash_flows(cash_flows, sort_by=SortColumn.POST_DATE)

    result = calculator._assign_factors(cash_flows, convention)

    assert result['factor'].notna().all()
    assert len(convention._calls) == 2
    assert convention._calls[0][0] == start_date + pd.Timedelta(days=1) # Advance: same date
    assert convention._calls[0][1] == start_date + pd.Timedelta(days=1)
    assert convention._calls[1][0] == start_date + pd.Timedelta(days=1) # Payment: advance value_date to payment value_date
    assert convention._calls[1][1] == date2
    assert result.loc[0, 'factor'].primary_period_fraction == 0.0
    assert abs(result.loc[1, 'factor'].primary_period_fraction - 30/365.0) < 1e-8

def test_assign_factors_charges_excluded(calculator):
    # Test Charges with include_non_financing_flows=False
    convention = MockConvention(use_post_dates=True, include_non_financing_flows=False)
    advance = SeriesAdvance(post_date_from=start_date, amount=1000.0)
    payment = SeriesPayment(post_date_from=date2, amount=1050.0)
    charge = SeriesCharge(post_date_from=date3, amount=50.0)
    cash_flows = create_cash_flows(calculator, [advance, payment, charge], start_date)
    cash_flows = calculator._sort_cash_flows(cash_flows, sort_by=SortColumn.POST_DATE)

    result = calculator._assign_factors(cash_flows, convention)

    assert result['factor'].notna().all()
    assert len(convention._calls) == 3
    assert convention._calls[2][0] == date3  # Charge: same date
    assert convention._calls[2][1] == date3
    assert result.loc[2, 'factor'].primary_period_fraction == 0.0

def test_assign_factors_charges_included(calculator):
    # Test Charges with include_non_financing_flows=True, using XIRR (DRAWDOWN origin)
    convention = MockConvention(
        use_post_dates=True,
        include_non_financing_flows=True,
        use_xirr_method=True)
    advance = SeriesAdvance(post_date_from=start_date, amount=1000.0) #"2026-01-01"
    payment = SeriesPayment(post_date_from=date2, amount=1050.0)      #"2026-02-01"
    charge = SeriesCharge(post_date_from=date3, amount=50.0)          #"2026-03-01"
    cash_flows = create_cash_flows(calculator, [advance, payment, charge], start_date)
    cash_flows = calculator._sort_cash_flows(cash_flows, sort_by=SortColumn.POST_DATE)

    result = calculator._assign_factors(cash_flows, convention)

    assert result['factor'].notna().all()
    assert len(convention._calls) == 3
    assert convention._calls[2][0] == start_date  # Charge: start to date3
    assert convention._calls[2][1] == date3
    assert abs(result.loc[2, 'factor'].primary_period_fraction - 59/365.0) < 1e-8

def test_assign_factors_predate_drawdown(calculator):
    # Test Cash Flow Predating Drawdown
    convention = MockConvention(use_post_dates=True)  # NEIGHBOUR origin by default
    advance = SeriesAdvance(post_date_from=date2, amount=1000.0)  # 2026-02-01
    payment = SeriesPayment(post_date_from=start_date, amount=1050.0)  # 2026-01-01
    cash_flows = create_cash_flows(calculator, [advance, payment], start_date)
    cash_flows = calculator._sort_cash_flows(cash_flows, sort_by=SortColumn.POST_DATE)

    result = calculator._assign_factors(cash_flows, convention)

    assert result['factor'].notna().all()
    assert len(convention._calls) == 2

    # Payment (index 0, post_date=2026-01-01, predates drawdown)
    assert convention._calls[0][0] == start_date  # Payment: same date
    assert convention._calls[0][1] == start_date
    assert result.loc[0, 'factor'].primary_period_fraction == 0.0

    # Advance (index 1, post_date=2026-02-01, at drawdown)
    assert convention._calls[1][0] == date2  # Advance: same date
    assert convention._calls[1][1] == date2
    assert result.loc[1, 'factor'].primary_period_fraction == 0.0

def test_assign_factors_no_advances(calculator):
    convention = MockConvention(use_post_dates=True)
    payment = SeriesPayment(post_date_from=start_date, amount=1050.0)
    cash_flows = create_cash_flows(calculator, [payment], start_date)

    with pytest.raises(ValidationError, match="At least one advance required"):
        calculator._assign_factors(cash_flows, convention)

def test_assign_factors_single_cash_flow(calculator):
    # Test Single Cash Flow
    convention = MockConvention(use_post_dates=True)
    advance = SeriesAdvance(post_date_from=start_date, amount=1000.0)
    cash_flows = create_cash_flows(calculator, [advance], start_date)

    result = calculator._assign_factors(cash_flows, convention)

    assert result['factor'].notna().all()
    assert len(convention._calls) == 1
    assert convention._calls[0][0] == start_date
    assert convention._calls[0][1] == start_date
    assert result.loc[0, 'factor'].primary_period_fraction == 0.0

def test_assign_factors_multiple_advances_same_date(calculator):
    convention = MockConvention(use_post_dates=True)  # NEIGHBOUR
    advance1 = SeriesAdvance(post_date_from=start_date, amount=600.0)
    advance2 = SeriesAdvance(
        post_date_from=start_date,
        value_date_from=start_date + pd.Timedelta(days=15),
        amount=400.0)
    payment = SeriesPayment(post_date_from=date2, amount=1000.0)
    cash_flows = create_cash_flows(calculator, [advance1, advance2, payment], start_date)
    cash_flows = calculator._sort_cash_flows(cash_flows, sort_by=SortColumn.POST_DATE)

    result = calculator._assign_factors(cash_flows, convention)

    assert result['factor'].notna().all()
    assert len(convention._calls) == 3
    # Advance 1: same date (drawdown)
    assert convention._calls[0][0] == start_date
    assert convention._calls[0][1] == start_date
    assert result.loc[0, 'factor'].primary_period_fraction == 0.0
    # Advance 2: same date (drawdown)
    assert convention._calls[1][0] == start_date
    assert convention._calls[1][1] == start_date
    assert result.loc[1, 'factor'].primary_period_fraction == 0.0
    # Payment: 31 days after drawdown
    assert convention._calls[2][0] == start_date
    assert convention._calls[2][1] == date2
    assert abs(result.loc[2, 'factor'].primary_period_fraction - 31/365.0) < 1e-8

def test_assign_factors_us30360_excluding_charges(calculator):
    convention = US30360(use_post_dates=True)  # NEIGHBOUR
    advance = SeriesAdvance(post_date_from=start_date, amount=1000.0)  # 2026-01-01
    charge = SeriesCharge(post_date_from=start_date, amount=10.0)  # 2026-01-01
    payment = SeriesPayment(post_date_from=date2, amount=1050.0)  # 2026-02-01
    cash_flows = create_cash_flows(calculator, [advance, charge, payment], start_date)
    cash_flows = calculator._sort_cash_flows(cash_flows, sort_by=SortColumn.POST_DATE)

    result = calculator._assign_factors(cash_flows, convention)

    assert result['factor'].notna().all()
    # Advance: drawdown
    assert result.loc[0, 'factor'].primary_period_fraction == 0.0
    # Charge: excluded
    assert result.loc[1, 'factor'].primary_period_fraction == 0.0
    # Payment: 30/360
    assert abs(result.loc[2, 'factor'].primary_period_fraction - 0.08333333333333333) < 1e-8
