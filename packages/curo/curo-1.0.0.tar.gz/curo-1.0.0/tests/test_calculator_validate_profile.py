# test_calculator_validate_profile.py
# pylint: disable=C0114,C0116,W0212,W0621
# - C0114: missing-module-docstring
# - C0116: missing-function-docstring
# - W0212: protected-access
# - W0621: redefined-outer-name

import pytest
import pandas as pd
import numpy as np
from curo.calculator import Calculator
from curo.enums import CashFlowColumn as Column, SortColumn, ValidationMode
from curo.exceptions import ValidationError
from curo.series import SeriesAdvance, SeriesPayment, SeriesCharge

@pytest.fixture
def calculator():
    return Calculator(precision=2)

@pytest.fixture
def valid_profile_solve_rate():
    # Profile for SOLVE_RATE: all amounts known, sorted by post_date
    advance = SeriesAdvance(
        number_of=1,
        amount=1000.0,
        post_date_from=pd.Timestamp("2025-01-01", tz="UTC"),
        label="Loan advance"
    )
    payment = SeriesPayment(
        number_of=1,
        amount=1050.0,
        post_date_from=pd.Timestamp("2025-12-31", tz="UTC"),
        is_interest_capitalised=True,
        label="Loan repayment"
    )
    charge = SeriesCharge(
        number_of=1,
        amount=50.0,
        post_date_from=pd.Timestamp("2025-01-01", tz="UTC"),
        label="Arrangement fee"
    )
    calc = Calculator(precision=2)
    calc.add(advance)
    calc.add(payment)
    calc.add(charge)
    profile = calc._build_profile(start_date=pd.Timestamp("2025-01-01", tz="UTC"))
    return calc._sort_cash_flows(profile, sort_by=SortColumn.POST_DATE)

@pytest.fixture
def valid_profile_solve_value():
    # Profile for SOLVE_VALUE: one unknown payment, sorted by post_date
    advance = SeriesAdvance(
        number_of=1,
        amount=1000.0,
        post_date_from=pd.Timestamp("2025-01-01", tz="UTC"),
        label="Loan advance"
    )
    payment = SeriesPayment(
        number_of=1,
        amount=None,  # Unknown
        post_date_from=pd.Timestamp("2025-12-31", tz="UTC"),
        is_interest_capitalised=True,
        label="Loan repayment",
        weighting=1.0
    )
    charge = SeriesCharge(
        number_of=1,
        amount=50.0,
        post_date_from=pd.Timestamp("2025-01-01", tz="UTC"),
        label="Arrangement fee"
    )
    calc = Calculator(precision=2)
    calc.add(advance)
    calc.add(payment)
    calc.add(charge)
    profile = calc._build_profile(start_date=pd.Timestamp("2025-01-01", tz="UTC"))
    return calc._sort_cash_flows(profile, sort_by=SortColumn.POST_DATE)

def test_valid_profile_solve_value(calculator, valid_profile_solve_value):
    calculator.profile = valid_profile_solve_value
    calculator._validate_profile(
        valid_profile_solve_value,
        sort_by=SortColumn.POST_DATE,
        mode=ValidationMode.SOLVE_VALUE
    )
    # No exception means success

def test_valid_profile_solve_rate(calculator, valid_profile_solve_rate):
    calculator.profile = valid_profile_solve_rate
    calculator._validate_profile(
        valid_profile_solve_rate,
        sort_by=SortColumn.POST_DATE,
        mode=ValidationMode.SOLVE_RATE
    )
    # No exception means success

def test_empty_profile(calculator):
    empty_df = pd.DataFrame(columns=[col.value for col in Column])
    with pytest.raises(ValidationError, match="Cash flow DataFrame is empty"):
        calculator._validate_profile(empty_df, sort_by=SortColumn.POST_DATE)

def test_missing_columns(calculator, valid_profile_solve_rate):
    invalid_df = valid_profile_solve_rate.drop(columns=[Column.AMOUNT.value])
    with pytest.raises(ValidationError, match="Missing required columns"):
        calculator._validate_profile(invalid_df, sort_by=SortColumn.POST_DATE)

def test_incorrect_dtype(calculator, valid_profile_solve_rate):
    invalid_df = valid_profile_solve_rate.copy()
    invalid_df[Column.AMOUNT.value] = invalid_df[Column.AMOUNT.value].astype("object")
    with pytest.raises(ValidationError, match="Column amount must have dtype float64"):
        calculator._validate_profile(invalid_df, sort_by=SortColumn.POST_DATE)

def test_nan_values(calculator, valid_profile_solve_rate):
    invalid_df = valid_profile_solve_rate.copy()
    invalid_df.loc[0, Column.AMOUNT.value] = np.nan
    with pytest.raises(ValidationError, match="Cash flow DataFrame contains NaN values"):
        calculator._validate_profile(invalid_df, sort_by=SortColumn.POST_DATE)

def test_negative_weighting(calculator, valid_profile_solve_rate):
    invalid_df = valid_profile_solve_rate.copy()
    invalid_df.loc[0, Column.WEIGHTING.value] = -1.0
    with pytest.raises(ValidationError, match="Weighting must be > 0"):
        calculator._validate_profile(invalid_df, sort_by=SortColumn.POST_DATE)

def test_value_date_before_post_date(calculator, valid_profile_solve_rate):
    invalid_df = valid_profile_solve_rate.copy()
    invalid_df.loc[0, Column.VALUE_DATE.value] = pd.Timestamp("2024-12-31", tz="UTC")
    with pytest.raises(ValidationError, match="value_date must be on or after post_date"):
        calculator._validate_profile(invalid_df, sort_by=SortColumn.POST_DATE)

def test_no_advances(calculator, valid_profile_solve_rate):
    invalid_df = valid_profile_solve_rate[
        valid_profile_solve_rate[Column.IS_INTEREST_CAPITALISED.value].notna() |
        valid_profile_solve_rate[Column.IS_CHARGE.value]
    ]
    with pytest.raises(ValidationError, match="At least one advance required"):
        calculator._validate_profile(invalid_df, sort_by=SortColumn.POST_DATE)

def test_no_payments(calculator, valid_profile_solve_rate):
    invalid_df = valid_profile_solve_rate[
        valid_profile_solve_rate[Column.IS_INTEREST_CAPITALISED.value].isna()
    ]
    with pytest.raises(ValidationError, match="At least one payment required"):
        calculator._validate_profile(invalid_df, sort_by=SortColumn.POST_DATE)

def test_payment_predates_advance(calculator, valid_profile_solve_rate):
    invalid_df = valid_profile_solve_rate.copy()
    invalid_df.loc[
        invalid_df[Column.IS_INTEREST_CAPITALISED.value].notna(),
        Column.POST_DATE.value
    ] = pd.Timestamp("2024-12-31", tz="UTC")
    with pytest.raises(ValidationError, match="Payment or charge post_date cannot predate"):
        calculator._validate_profile(invalid_df, sort_by=SortColumn.POST_DATE)

def test_negative_charge(calculator, valid_profile_solve_rate):
    invalid_df = valid_profile_solve_rate.copy()
    invalid_df.loc[invalid_df[Column.IS_CHARGE.value], Column.AMOUNT.value] = -50.0
    with pytest.raises(ValidationError, match="Charge amounts must be non-negative"):
        calculator._validate_profile(invalid_df, sort_by=SortColumn.POST_DATE)

def test_unknown_charge(calculator, valid_profile_solve_rate):
    invalid_df = valid_profile_solve_rate.copy()
    invalid_df.loc[invalid_df[Column.IS_CHARGE.value], Column.IS_KNOWN.value] = False
    invalid_df.loc[invalid_df[Column.IS_CHARGE.value], Column.AMOUNT.value] = 0.0
    with pytest.raises(ValidationError, match="Charge values must be known"):
        calculator._validate_profile(invalid_df, sort_by=SortColumn.POST_DATE)

def test_charge_postdates_payment(calculator, valid_profile_solve_rate):
    invalid_df = valid_profile_solve_rate.copy()
    invalid_df.loc[
        invalid_df[Column.IS_CHARGE.value],
        [Column.POST_DATE.value, Column.VALUE_DATE.value]
    ] = pd.Timestamp("2026-01-01", tz="UTC")
    with pytest.raises(ValidationError, match="Charge post_date cannot postdate"):
        calculator._validate_profile(invalid_df, sort_by=SortColumn.POST_DATE)

def test_last_payment_no_interest_capitalisation(calculator, valid_profile_solve_rate):
    invalid_df = valid_profile_solve_rate.copy()
    invalid_df.loc[
        invalid_df[Column.IS_INTEREST_CAPITALISED.value].notna(),
        Column.IS_INTEREST_CAPITALISED.value
    ] = False
    with pytest.raises(ValidationError,
                       match="Interest and capital repayment cash flow end dates misaligned"):
        calculator._validate_profile(invalid_df, sort_by=SortColumn.POST_DATE)

def test_solve_value_no_unknowns(calculator, valid_profile_solve_rate):
    with pytest.raises(ValidationError,
                       match="At least one unknown advance or payment value required"):
        calculator._validate_profile(
            valid_profile_solve_rate,
            sort_by=SortColumn.POST_DATE,
            mode=ValidationMode.SOLVE_VALUE
        )

def test_solve_value_mixed_unknowns(calculator, valid_profile_solve_value):
    invalid_df = valid_profile_solve_value.copy()
    invalid_df.loc[
        (invalid_df[Column.IS_INTEREST_CAPITALISED.value].isna() &
         ~invalid_df[Column.IS_CHARGE.value]),
        [Column.IS_KNOWN.value, Column.AMOUNT.value]
    ] = [False, 0.0]
    with pytest.raises(ValidationError,
                       match="Unknowns must be either all advances or all payments"):
        calculator._validate_profile(
            invalid_df,
            sort_by=SortColumn.POST_DATE,
            mode=ValidationMode.SOLVE_VALUE
        )

def test_solve_rate_has_unknowns(calculator, valid_profile_solve_value):
    with pytest.raises(ValidationError, match="All values must be known in SOLVE_RATE mode"):
        calculator._validate_profile(
            valid_profile_solve_value,
            sort_by=SortColumn.POST_DATE,
            mode=ValidationMode.SOLVE_RATE
        )

def test_unsorted_profile(calculator, valid_profile_solve_rate):
    invalid_df = valid_profile_solve_rate.sort_values(by=Column.POST_DATE.value, ascending=False)
    with pytest.raises(ValidationError, match="Cash flows must be sorted by post_date"):
        calculator._validate_profile(
            invalid_df,
            sort_by=SortColumn.POST_DATE,
            mode=ValidationMode.SOLVE_RATE
        )

def test_valid_profile_value_date_sort(calculator, valid_profile_solve_rate):
    # Test sorting by value_date
    sorted_profile = calculator._sort_cash_flows(
        valid_profile_solve_rate, sort_by=SortColumn.VALUE_DATE)
    calculator._validate_profile(
        sorted_profile,
        sort_by=SortColumn.VALUE_DATE,
        mode=ValidationMode.SOLVE_RATE
    )
    # No exception means success

def test_invalid_is_interest_capitalised_payment(calculator, valid_profile_solve_value):
    """Test that is_interest_capitalised must be True/False for payments (line 477)."""
    invalid_df = valid_profile_solve_value.copy()
    invalid_df.loc[
        invalid_df[Column.IS_INTEREST_CAPITALISED.value].notna(),
        Column.IS_INTEREST_CAPITALISED.value
    ] = "invalid"
    with pytest.raises(
        ValidationError,
        match="is_interest_capitalised must be True or False for payments"):
        calculator._validate_profile(
            invalid_df,
            sort_by=SortColumn.POST_DATE,
            mode=ValidationMode.SOLVE_VALUE)

def test_invalid_is_interest_capitalised_non_payment(calculator, valid_profile_solve_value):
    """Test that is_interest_capitalised must be None for advances/charges (line 480)."""
    invalid_df = valid_profile_solve_value.copy()
    invalid_df.loc[
        invalid_df[Column.IS_INTEREST_CAPITALISED.value].isna(),
        Column.IS_INTEREST_CAPITALISED.value
    ] = True
    with pytest.raises(
        ValidationError,
        match="is_interest_capitalised must be None for advances and charges"):
        calculator._validate_profile(
            invalid_df,
            sort_by=SortColumn.POST_DATE,
            mode=ValidationMode.SOLVE_VALUE)

def test_solve_value_non_zero_unknown(calculator, valid_profile_solve_value):
    """Test that unknown values must be 0.0 in SOLVE_VALUE mode (line 551)."""
    invalid_df = valid_profile_solve_value.copy()
    invalid_df.loc[
        ~invalid_df[Column.IS_KNOWN.value],
        Column.AMOUNT.value
    ] = 100.0  # Non-zero unknown
    with pytest.raises(
        ValidationError,
        match="Unknown values must be 0.0 \\(placeholder\\) in SOLVE_VALUE mode"):
        calculator._validate_profile(
            invalid_df,
            sort_by=SortColumn.POST_DATE,
            mode=ValidationMode.SOLVE_VALUE)
