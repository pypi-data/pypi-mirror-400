# test_calculator.py
# pylint: disable=C0114,C0116,C0301,W0212,W0621
# - C0114: missing-module-docstring
# - C0116: missing-function-docstring
# - C0301: line-too-long
# - W0212: protected-access
# - W0621: redefined-outer-name

import pytest
import pandas as pd
from curo.calculator import Calculator
from curo.daycount.us_30u_360 import US30U360
from curo.daycount.us_appendix_j import USAppendixJ
from curo.enums import (
    CashFlowColumn as Column,
    CashFlowColumnExtras as ColumnExtras,
    Mode)
from curo.exceptions import ValidationError
from curo.series import SeriesAdvance, SeriesPayment, SeriesCharge

@pytest.fixture
def valid_series():
    return SeriesAdvance(
        number_of=1,
        amount=1000.0,
        post_date_from=pd.Timestamp("2025-01-01", tz="UTC"),
        label="Loan advance"
    )

@pytest.fixture
def valid_profile():
    return pd.DataFrame({
        Column.POST_DATE.value: [pd.Timestamp("2025-01-01", tz="UTC")],
        Column.VALUE_DATE.value: [pd.Timestamp("2025-01-01", tz="UTC")],
        Column.AMOUNT.value: [1000.0],
        Column.IS_KNOWN.value: [True],
        Column.WEIGHTING.value: [1.0],
        Column.LABEL.value: ["Loan advance"],
        Column.MODE.value: ["advance"],
        Column.IS_INTEREST_CAPITALISED.value: [None],
        Column.IS_CHARGE.value: [False]
    })

def test_constructor_valid_precision():
    calc = Calculator(precision=2)
    assert calc.precision == 2
    assert calc.profile is None
    assert not calc._series
    assert calc._is_bespoke_profile is False

def test_constructor_invalid_precision():
    with pytest.raises(ValidationError, match="Precision must be between 0 and 4"):
        Calculator(precision=5)
    with pytest.raises(ValidationError, match="Precision must be between 0 and 4"):
        Calculator(precision=-1)

def test_constructor_with_profile(valid_profile):
    calc = Calculator(precision=3, profile=valid_profile)
    assert calc.precision == 3
    assert calc.profile.equals(valid_profile)
    assert not calc._series
    assert calc._is_bespoke_profile is True

def test_add_valid_series(valid_series):
    calc = Calculator(precision=2)
    calc.add(valid_series)
    assert len(calc._series) == 1
    assert calc._series[0] == valid_series
    assert calc._series[0].amount == 1000.0  # Amount unchanged

def test_add_series_with_rounding():
    calc = Calculator(precision=1)
    series = SeriesPayment(
        number_of=1,
        amount=123.456,
        post_date_from=pd.Timestamp("2025-01-01", tz="UTC"),
        label="Loan repayment"
    )
    calc.add(series)
    assert len(calc._series) == 1
    assert calc._series[0].amount == 123.5  # Rounded to 1 decimal place

def test_add_series_with_bespoke_profile(valid_profile):
    calc = Calculator(precision=2, profile=valid_profile)
    series = SeriesCharge(
        number_of=1,
        amount=50.0,
        post_date_from=pd.Timestamp("2025-01-01", tz="UTC"),
        label="Arrangement fee"
    )
    with pytest.raises(ValidationError, match="Cannot add series with a bespoke profile"):
        calc.add(series)

def test_add_solve_value_solve_rate_different_conventions():
    """Test solve_value with US30U360 and solve_rate with USAppendixJ."""
    calc = Calculator(precision=2)
    calc.add(SeriesAdvance(amount=1000.0, post_date_from=pd.Timestamp("2025-01-01", tz="UTC")))
    calc.add(SeriesPayment(amount=None, mode=Mode.ARREAR))
    payment = calc.solve_value(
        convention=US30U360(),
        interest_rate=0.1,
        start_date=pd.Timestamp("2025-01-01", tz="UTC")
    )
    assert abs(payment - 1008.33) < 1e-6, f"Expected payment ~1008.33, got {payment}"

    # Verify profile has factor column and mixed is_known values
    assert ColumnExtras.FACTOR.value in calc.profile.columns, "Profile missing factor column"
    assert not calc.profile[Column.IS_KNOWN.value].all(), "Profile should have is_known=False for payment"

    irr = calc.solve_rate(
        convention=USAppendixJ(),
        start_date=pd.Timestamp("2025-01-01", tz="UTC")
    )
    expected_irr = 0.09995999480755229
    assert abs(irr - expected_irr) < 1e-6, f"Expected IRR ~{expected_irr}, got {irr}"

    # Verify is_known semantics preserved in self.profile
    assert calc.profile[Column.IS_KNOWN.value].eq(True).all()

def test_solve_rate_reuses_profile():
    """Test that solve_rate reuses self.profile from solve_value."""
    calc = Calculator(precision=2)
    calc.add(SeriesAdvance(amount=1000.0, post_date_from=pd.Timestamp("2025-01-01", tz="UTC")))
    calc.add(SeriesPayment(amount=None, mode=Mode.ARREAR))
    calc.solve_value(
        convention=US30U360(),
        interest_rate=0.1,
        start_date=pd.Timestamp("2025-01-01", tz="UTC")
    )
    original_profile = calc.profile.copy()
    irr = calc.solve_rate(
        convention=USAppendixJ(),
        start_date=pd.Timestamp("2025-01-01", tz="UTC")
    )
    assert abs(irr - 0.09995999480755229) < 1e-6, f"Expected IRR ~0.09995999480755229, got {irr}"

    # Verify profile structure (same rows, updated factors)
    assert calc.profile[Column.POST_DATE.value].equals(original_profile[Column.POST_DATE.value]), "Profile dates changed"
    assert calc.profile[Column.AMOUNT.value].equals(original_profile[Column.AMOUNT.value]), "Profile amounts changed"
    assert not calc.profile[ColumnExtras.FACTOR.value].equals(original_profile[ColumnExtras.FACTOR.value]), "Factors not updated for new convention"

def test_multiple_solve_value_calls():
    """Test solve_rate after multiple solve_value calls with different conventions."""
    calc = Calculator(precision=2)
    calc.add(SeriesAdvance(amount=1000.0, post_date_from=pd.Timestamp("2025-01-01", tz="UTC")))
    calc.add(SeriesPayment(amount=None, mode=Mode.ARREAR))

    # First solve_value with US30U360
    payment1 = calc.solve_value(
        convention=US30U360(),
        interest_rate=0.1,
        start_date=pd.Timestamp("2025-01-01", tz="UTC")
    )
    assert abs(payment1 - 1008.33) < 1e-6, f"Expected payment ~1008.33, got {payment1}"

    # Second solve_value with USAppendixJ
    payment2 = calc.solve_value(
        convention=USAppendixJ(),
        interest_rate=0.1,
        start_date=pd.Timestamp("2025-01-01", tz="UTC")
    )
    assert abs(payment2 - 1008.33) < 1e-6, f"Expected payment ~1008.33, got {payment2}"
    irr = calc.solve_rate(
        convention=USAppendixJ(),
        start_date=pd.Timestamp("2025-01-01", tz="UTC")
    )
    assert abs(irr - 0.09995999480755229) < 1e-6, f"Expected IRR ~0.09995999480755229, got {irr}"

    # Verify is_known updated to True for all unknowns by solve_rate
    assert calc.profile[Column.IS_KNOWN.value].eq(True).all()
