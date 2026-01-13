# test_calculator_build_schedule.py
# pylint: disable=C0114,C0116,W0212,W0621
# - C0114: missing-module-docstring
# - C0116: missing-function-docstring
# - W0212: protected-access
# - W0621: redefined-outer-name

import pytest
import pandas as pd
from curo.calculator import Calculator
from curo.daycount.day_count_factor import DayCountFactor
from curo.daycount.us_30_360 import US30360
from curo.daycount.us_appendix_j import USAppendixJ
from curo.enums import (
    CashFlowColumn as Column,
    CashFlowColumnExtras as ColumnExtras,
    Frequency
    )
from curo.exceptions import ValidationError
from curo.series import SeriesAdvance, SeriesPayment, SeriesCharge

# Fixture for a valid profile from solve_rate
@pytest.fixture
def valid_profile_solve_rate():
    calc = Calculator(precision=2)
    advance = SeriesAdvance(
        amount=10000,
        post_date_from=pd.Timestamp('2026-01-04', tz='UTC')
    )
    payment = SeriesPayment(
        number_of=3,
        amount=3379.27,
        frequency=Frequency.MONTHLY,
        post_date_from=pd.Timestamp('2026-02-04', tz='UTC')
    )
    calc.add(advance)
    calc.add(payment)
    profile = calc._build_profile(start_date=pd.Timestamp('2026-01-04', tz='UTC'))
    return profile, calc

# Fixture for a valid profile from solve_value
@pytest.fixture
def valid_profile_solve_value():
    calc = Calculator(precision=2)
    advance = SeriesAdvance(
        amount=10000,
        post_date_from=pd.Timestamp('2026-01-04', tz='UTC')
    )
    payment = SeriesPayment(
        number_of=3,
        amount=None,
        frequency=Frequency.MONTHLY,
        post_date_from=pd.Timestamp('2026-02-04', tz='UTC')
    )
    calc.add(advance)
    calc.add(payment)
    profile = calc._build_profile(start_date=pd.Timestamp('2026-01-04', tz='UTC'))
    return profile, calc

def test_build_schedule_missing_factor_column():
    """Test error for missing 'factor' column in profile."""
    calc = Calculator(precision=2)
    profile = pd.DataFrame({
        Column.POST_DATE.value: [
            pd.Timestamp('2026-01-04', tz='UTC'),
            pd.Timestamp('2026-02-04', tz='UTC')],
        Column.VALUE_DATE.value: [
            pd.Timestamp('2026-01-04', tz='UTC'),
            pd.Timestamp('2026-02-04', tz='UTC')],
        Column.AMOUNT.value: [-10000.0, 10500.0],
        Column.IS_KNOWN.value: [True, True],
        Column.WEIGHTING.value: [1.0, 1.0],
        Column.LABEL.value: ['Loan', 'Instalment'],
        Column.MODE.value: ['advance', 'arrear'],
        Column.IS_INTEREST_CAPITALISED.value: [None, True],
        Column.IS_CHARGE.value: [False, False]
    })
    with pytest.raises(
        ValidationError,
        match="Cash flow profile must include a 'factor' column"):
        calc.build_schedule(profile, US30360(), interest_rate=0.12)

def test_build_schedule_amortization_valid_solve_rate(valid_profile_solve_rate):
    """Test Amortization schedule generation from solve_rate profile."""
    profile, calc = valid_profile_solve_rate
    convention = US30360()
    profile = calc._assign_factors(profile, convention)
    schedule = calc.build_schedule(profile, convention, interest_rate=0.12)
    # Verify columns
    expected_columns = [
        Column.POST_DATE.value,
        Column.LABEL.value,
        Column.AMOUNT.value,
        ColumnExtras.CAPITAL.value,
        ColumnExtras.INTEREST.value,
        ColumnExtras.CAPITAL_BALANCE.value
        ]
    assert list(schedule.columns) == expected_columns
    # Verify data types
    assert schedule[Column.AMOUNT.value].dtype == 'float64'
    assert schedule[ColumnExtras.CAPITAL.value].dtype == 'float64'
    assert schedule[ColumnExtras.INTEREST.value].dtype == 'float64'
    assert schedule[ColumnExtras.CAPITAL_BALANCE.value].dtype == 'float64'
    # Verify capital_balance nets to zero (within precision)
    assert abs(schedule[ColumnExtras.CAPITAL_BALANCE.value].iloc[-1]) < 1e-6
    # Verify amounts and calculations
    assert schedule[Column.AMOUNT.value].iloc[0] == -10000.0  # Advance
    assert schedule[Column.AMOUNT.value].iloc[1:].eq(3379.27).all()  # Payments
    assert ((
        schedule[ColumnExtras.CAPITAL.value] -
        schedule[ColumnExtras.INTEREST.value])).eq(schedule[Column.AMOUNT.value]).all()

def test_build_schedule_apr_valid_solve_rate(valid_profile_solve_rate):
    """Test APR proof schedule generation from solve_rate profile."""
    profile, calc = valid_profile_solve_rate
    convention = US30360(use_xirr_method=True)
    profile = calc._assign_factors(profile, convention)
    schedule = calc.build_schedule(profile, convention, interest_rate=0.08568955)
    # Verify columns
    expected_columns = [
        Column.POST_DATE.value,
        Column.LABEL.value,
        Column.AMOUNT.value,
        ColumnExtras.DISCOUNT_LOG.value,
        ColumnExtras.AMOUNT_DISCOUNTED.value,
        ColumnExtras.DISCOUNTED_BALANCE.value
        ]
    assert list(schedule.columns) == expected_columns
    # Verify data types
    assert schedule[Column.AMOUNT.value].dtype == 'float64'
    assert schedule[ColumnExtras.AMOUNT_DISCOUNTED.value].dtype == 'float64'
    assert schedule[ColumnExtras.DISCOUNTED_BALANCE.value].dtype == 'float64'
    assert schedule[ColumnExtras.DISCOUNT_LOG.value].dtype == 'object'
    # Verify discounted_balance nets to zero
    assert schedule[ColumnExtras.DISCOUNTED_BALANCE.value].iloc[-1] < 1e-6
    # Verify amounts
    assert schedule[Column.AMOUNT.value].iloc[0] == -10000.0
    assert schedule[Column.AMOUNT.value].iloc[1:].eq(3379.27).all()

def test_build_schedule_amortization_valid_solve_value(valid_profile_solve_value):
    """Test Amortization schedule generation from solve_value profile."""
    profile, calc = valid_profile_solve_value
    convention = US30360()
    profile = calc._assign_factors(profile, convention)
    interest_rate = 0.12
    calc.solve_value(convention,interest_rate)
    schedule = calc.build_schedule(profile, convention, interest_rate=0.12)
    # Verify IS_KNOWN set to True
    assert profile[Column.IS_KNOWN.value].eq(False).any()  # Original has False
    #assert schedule[Column.IS_KNOWN.value].all()  # Doesn't expose column
    # Verify columns and data
    expected_columns = [
        Column.POST_DATE.value,
        Column.LABEL.value,
        Column.AMOUNT.value,
        ColumnExtras.CAPITAL.value,
        ColumnExtras.INTEREST.value,
        ColumnExtras.CAPITAL_BALANCE.value
        ]
    assert list(schedule.columns) == expected_columns
    assert schedule['capital_balance'].iloc[-1] < 1e-6
    assert not schedule['amount'].isna().any()

def test_build_schedule_apr_valid_solve_value(valid_profile_solve_value):
    """Test APR proof schedule generation from solve_value profile."""
    profile, calc = valid_profile_solve_value
    convention = US30360(use_xirr_method=True)
    profile = calc._assign_factors(profile, convention)
    interest_rate = 0.12
    calc.solve_value(convention, interest_rate)
    schedule = calc.build_schedule(calc.profile, convention, interest_rate)
    # Verify IS_KNOWN set to True
    assert profile[Column.IS_KNOWN.value].eq(False).any()
    #assert schedule[Column.IS_KNOWN.value].all()  # Doesn't expose column
    # Verify columns and data
    expected_columns = [
        Column.POST_DATE.value,
        Column.LABEL.value,
        Column.AMOUNT.value,
        ColumnExtras.DISCOUNT_LOG.value,
        ColumnExtras.AMOUNT_DISCOUNTED.value,
        ColumnExtras.DISCOUNTED_BALANCE.value
    ]
    assert list(schedule.columns) == expected_columns
    assert schedule[ColumnExtras.DISCOUNTED_BALANCE.value].iloc[-1] < 1e-6
    assert not schedule[Column.AMOUNT.value].isna().any()

def test_build_schedule_with_zero_solved_amount(valid_profile_solve_value):
    """Test handling of legitimate zero solved amounts."""
    profile, calc = valid_profile_solve_value
    profile = calc._assign_factors(profile, US30360())
    # Simulate a zero solved amount
    profile.loc[profile[Column.LABEL.value] == 'Instalment', Column.AMOUNT.value] = 0.0
    schedule = calc.build_schedule(profile, US30360(), interest_rate=0.12)
    # Verify schedule is generated
    assert not schedule.empty
    #assert schedule[Column.IS_KNOWN.value].all()  # Doesn't expose column
    assert schedule['amount'].eq(0.0).any()  # Zero amounts present

def test_build_schedule_negative_interest_rate():
    """Test error for negative interest rate."""
    calc = Calculator(precision=2)
    profile = pd.DataFrame({
        Column.POST_DATE.value: [
            pd.Timestamp('2026-01-04', tz='UTC'),
            pd.Timestamp('2026-02-04', tz='UTC')],
        Column.VALUE_DATE.value: [
            pd.Timestamp('2026-01-04', tz='UTC'),
            pd.Timestamp('2026-02-04', tz='UTC')],
        Column.AMOUNT.value: [-10000.0, 10500.0],
        Column.IS_KNOWN.value: [True, True],
        Column.WEIGHTING.value: [1.0, 1.0],
        Column.LABEL.value: ['Loan', 'Instalment'],
        Column.MODE.value: ['advance', 'arrear'],
        Column.IS_INTEREST_CAPITALISED.value: [None, True],
        Column.IS_CHARGE.value: [False, False]
    })
    with pytest.raises(ValidationError, match="Negative interest rate not permitted"):
        calc.build_schedule(profile, US30360(), interest_rate=-0.12)

def test_build_schedule_nan_amount():
    """Test error for NaN amounts."""
    calc = Calculator(precision=2)
    profile = pd.DataFrame({
        Column.POST_DATE.value: [
            pd.Timestamp('2026-01-04', tz='UTC'),
            pd.Timestamp('2026-02-04', tz='UTC')],
        Column.VALUE_DATE.value: [
            pd.Timestamp('2026-01-04', tz='UTC'),
            pd.Timestamp('2026-02-04', tz='UTC')],
        Column.AMOUNT.value: [-10000.0, float('nan')],
        Column.IS_KNOWN.value: [True, False],
        Column.WEIGHTING.value: [1.0, 1.0],
        Column.LABEL.value: ['Loan', 'Instalment'],
        Column.MODE.value: ['advance', 'arrear'],
        Column.IS_INTEREST_CAPITALISED.value: [None, True],
        Column.IS_CHARGE.value: [False, False]
    })
    profile = calc._assign_factors(profile, US30360())
    with pytest.raises(ValidationError, match="All cash flow amounts must be defined"):
        calc.build_schedule(profile, US30360(), interest_rate=0.12)

def test_build_schedule_empty_profile():
    """Test error for empty profile."""
    calc = Calculator(precision=2)
    profile = pd.DataFrame(columns=[
        Column.POST_DATE.value, Column.VALUE_DATE.value, Column.AMOUNT.value,
        Column.IS_KNOWN.value, Column.WEIGHTING.value, Column.LABEL.value,
        Column.MODE.value, Column.IS_INTEREST_CAPITALISED.value, Column.IS_CHARGE.value,
        ColumnExtras.FACTOR.value
    ]).astype({
        Column.POST_DATE.value: 'datetime64[ns, UTC]',
        Column.VALUE_DATE.value: 'datetime64[ns, UTC]',
        Column.AMOUNT.value: 'float64',
        Column.IS_KNOWN.value: 'bool',
        Column.WEIGHTING.value: 'float64',
        Column.LABEL.value: 'object',
        Column.MODE.value: 'object',
        Column.IS_INTEREST_CAPITALISED.value: 'object',
        Column.IS_CHARGE.value: 'bool',
        ColumnExtras.FACTOR.value: 'object'
    })
    with pytest.raises(ValidationError, match="Cash flow DataFrame is empty"):
        calc.build_schedule(profile, US30360(), interest_rate=0.12)

def test_build_schedule_with_charges_amortization():
    """Test Amortization schedule with charges (should be skipped)."""
    calc = Calculator(precision=2)
    advance = SeriesAdvance(
        amount=10000,
        post_date_from=pd.Timestamp('2026-01-04', tz='UTC'))
    payment = SeriesPayment(
        number_of=3,
        amount=3379.27,
        frequency=Frequency.MONTHLY,
        post_date_from=pd.Timestamp('2026-02-04', tz='UTC'))
    charge = SeriesCharge(
        amount=100.0,
        post_date_from=pd.Timestamp('2026-02-04', tz='UTC'))
    calc.add(advance)
    calc.add(payment)
    calc.add(charge)
    profile = calc._build_profile(start_date=pd.Timestamp('2026-01-04', tz='UTC'))
    profile = calc._assign_factors(profile, US30360())
    schedule = calc.build_schedule(profile, US30360(), interest_rate=0.12)
    # Verify charges are not included in calculations
    assert not schedule[
        schedule[Column.LABEL.value] == charge.label].empty  # Charge is in profile
    assert abs(
        schedule[ColumnExtras.CAPITAL_BALANCE.value].iloc[-1]) < 1e-6  # Balance still nets to zero

def test_build_schedule_usappendixj_apr():
    """Test APR proof schedule with USAppendixJ convention."""
    calc = Calculator(precision=2)
    advance = SeriesAdvance(
        amount=10000,
        post_date_from=pd.Timestamp('2026-01-04', tz='UTC'))
    payment = SeriesPayment(
        number_of=3,
        amount=3379.27,
        frequency=Frequency.MONTHLY,
        post_date_from=pd.Timestamp('2026-02-04', tz='UTC'))
    calc.add(advance)
    calc.add(payment)
    profile = calc._build_profile(start_date=pd.Timestamp('2026-01-04', tz='UTC'))
    convention = USAppendixJ()
    profile = calc._assign_factors(profile, convention)
    schedule = calc.build_schedule(profile, convention, interest_rate=0.08249760)#0.12)
    # Verify USAppendixJ-specific calculations
    assert schedule[
        ColumnExtras.DISCOUNTED_BALANCE.value].iloc[-1] < 1e-6
    assert schedule[ # Check discount_log format
        ColumnExtras.DISCOUNT_LOG.value].str.contains('t = 2 : f = 0 : p = 12').any()

def test_build_schedule_high_interest_rate():
    """Test numerical stability with high interest rate."""
    calc = Calculator(precision=2)
    profile = pd.DataFrame({
        Column.POST_DATE.value: [
            pd.Timestamp('2026-01-04', tz='UTC'),
            pd.Timestamp('2026-02-04', tz='UTC')],
        Column.VALUE_DATE.value: [
            pd.Timestamp('2026-01-04', tz='UTC'),
            pd.Timestamp('2026-02-04', tz='UTC')],
        Column.AMOUNT.value: [-10000.0, 20000.0],
        Column.IS_KNOWN.value: [True, True],
        Column.WEIGHTING.value: [1.0, 1.0],
        Column.LABEL.value: ['Loan', 'Instalment'],
        Column.MODE.value: ['advance', 'arrear'],
        Column.IS_INTEREST_CAPITALISED.value: [None, True],
        Column.IS_CHARGE.value: [False, False],
        ColumnExtras.FACTOR.value: [
            DayCountFactor(primary_period_fraction=0.0),
            DayCountFactor(primary_period_fraction=1/12)]
    })
    schedule = calc.build_schedule(profile, US30360(), interest_rate=10.0)
    assert not schedule.empty
    assert abs(schedule[ColumnExtras.CAPITAL_BALANCE.value].iloc[-1]) < 1e-6

def test_build_schedule_all_zero_amounts():
    """Test handling of all zero amounts (valid if non-NaN)."""
    calc = Calculator(precision=2)
    profile = pd.DataFrame({
        Column.POST_DATE.value: [
            pd.Timestamp('2026-01-04', tz='UTC'),
            pd.Timestamp('2026-02-04', tz='UTC')],
        Column.VALUE_DATE.value: [
            pd.Timestamp('2026-01-04', tz='UTC'),
            pd.Timestamp('2026-02-04', tz='UTC')],
        Column.AMOUNT.value: [0.0, 0.0],
        Column.IS_KNOWN.value: [True, False],
        Column.WEIGHTING.value: [1.0, 1.0],
        Column.LABEL.value: ['Loan', 'Instalment'],
        Column.MODE.value: ['advance', 'arrear'],
        Column.IS_INTEREST_CAPITALISED.value: [None, True],
        Column.IS_CHARGE.value: [False, False],
        ColumnExtras.FACTOR.value: [
            DayCountFactor(primary_period_fraction=0.0),
            DayCountFactor(primary_period_fraction=1/12)]
    })
    schedule = calc.build_schedule(profile, US30360(), interest_rate=0.12)
    assert schedule[Column.AMOUNT.value].eq(0.0).all()
