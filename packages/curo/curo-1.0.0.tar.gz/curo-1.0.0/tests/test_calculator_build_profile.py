# test_calculator_build_profile.py
# pylint: disable=C0114,C0116,C0121,W0212,W0621
# - C0114: missing-module-docstring
# - C0116: missing-function-docstring
# - C0121: singleton-comparison
# - W0212: protected-access
# - W0621: redefined-outer-name

import pytest
import pandas as pd
from curo.calculator import Calculator
from curo.enums import CashFlowColumn as Column, Frequency, Mode
from curo.series import SeriesAdvance, SeriesPayment, SeriesCharge

@pytest.fixture
def calculator():
    return Calculator(precision=2)

# @pytest.fixture
# def start_date():
#     return pd.Timestamp("2025-01-01", tz="UTC")

# Common dates
start_date = pd.Timestamp("2025-01-01", tz="UTC")
date2 = pd.Timestamp("2025-02-01", tz="UTC")
date3 = pd.Timestamp("2025-03-01", tz="UTC")


def test_build_profile_empty_series(calculator):
    """Test building profile with empty series list."""
    profile = calculator._build_profile()
    assert profile.empty
    assert list(profile.columns) == [col.value for col in Column]
    assert profile.dtypes.to_dict() == {
        Column.POST_DATE.value: 'datetime64[ns, UTC]',
        Column.VALUE_DATE.value: 'datetime64[ns, UTC]',
        Column.AMOUNT.value: 'float64',
        Column.IS_KNOWN.value: 'bool',
        Column.WEIGHTING.value: 'float64',
        Column.LABEL.value: 'object',
        Column.MODE.value: 'object',
        Column.IS_INTEREST_CAPITALISED.value: 'object',
        Column.IS_CHARGE.value: 'bool'
    }

def test_build_profile_single_advance_dated(calculator):
    """Test building profile with a single dated advance."""
    advance = SeriesAdvance(
        number_of=1,
        amount=1000.0,
        post_date_from=start_date,
        label="Loan advance"
    )
    calculator.add(advance)
    profile = calculator._build_profile(start_date)
    assert len(profile) == 1
    assert profile.iloc[0].to_dict() == {
        Column.POST_DATE.value: start_date,
        Column.VALUE_DATE.value: start_date,
        Column.AMOUNT.value: -1000.0,  # Negated
        Column.IS_KNOWN.value: True,
        Column.WEIGHTING.value: 1.0,
        Column.LABEL.value: "Loan advance",
        Column.MODE.value: "advance",
        Column.IS_INTEREST_CAPITALISED.value: None,
        Column.IS_CHARGE.value: False
    }

def test_build_profile_single_payment_undated(calculator):
    """Test building profile with a single undated payment."""
    payment = SeriesPayment(
        number_of=1,
        amount=1050.0,
        is_interest_capitalised=True,
        label="Loan repayment"
    )
    calculator.add(payment)
    profile = calculator._build_profile(start_date)
    assert len(profile) == 1
    assert profile.iloc[0][Column.POST_DATE.value] == start_date
    assert profile.iloc[0][Column.AMOUNT.value] == 1050.0
    assert profile.iloc[0][Column.IS_INTEREST_CAPITALISED.value] is True
    assert profile.iloc[0][Column.IS_CHARGE.value] == False

def test_build_profile_multiple_series(calculator):
    """Test building profile with multiple series (advance, payment, charge)."""
    advance = SeriesAdvance(
        number_of=1,
        amount=1000.0,
        post_date_from=start_date,
        label="Loan advance"
    )
    payment = SeriesPayment(
        number_of=1,
        amount=1050.0,
        post_date_from=start_date + pd.Timedelta(days=365),
        is_interest_capitalised=True,
        label="Loan repayment"
    )
    charge = SeriesCharge(
        number_of=1,
        amount=50.0,
        post_date_from=start_date,
        label="Arrangement fee"
    )
    calculator.add(advance)
    calculator.add(payment)
    calculator.add(charge)
    profile = calculator._build_profile(start_date)
    assert len(profile) == 3
    assert (profile[Column.AMOUNT.value] == [-1000.0, 1050.0, 50.0]).all()
    assert (profile[Column.IS_CHARGE.value] == [False, False, True]).all()
    assert profile[Column.IS_INTEREST_CAPITALISED.value].to_list() == [None, True, None]

def test_build_profile_undated_arrear_mode(calculator):
    """Test undated series with Mode.ARREAR date rolling."""
    advance = SeriesAdvance(
        number_of=2,
        amount=500.0,
        frequency=Frequency.MONTHLY,
        mode=Mode.ARREAR
    )
    calculator.add(advance)
    profile = calculator._build_profile(pd.Timestamp("2025-01-01", tz="UTC"))
    assert len(profile) == 2
    assert profile[Column.POST_DATE.value].to_list() == [
        pd.Timestamp("2025-02-01", tz="UTC"),
        pd.Timestamp("2025-03-01", tz="UTC")
    ]

def test_build_profile_undated_advance_mode(calculator):
    """Test undated series with Mode.ADVANCE date rolling."""
    payment = SeriesPayment(
        number_of=2,
        amount=500.0,
        frequency=Frequency.MONTHLY,
        mode=Mode.ADVANCE,
        is_interest_capitalised=True
    )
    calculator.add(payment)
    profile = calculator._build_profile(pd.Timestamp("2025-01-01", tz="UTC"))
    assert len(profile) == 2
    assert profile[Column.POST_DATE.value].to_list() == [
        pd.Timestamp("2025-01-01", tz="UTC"),
        pd.Timestamp("2025-02-01", tz="UTC")
    ]

def test_build_profile_none_start_date(calculator):
    """Test building profile with None start_date (uses current date)."""
    advance = SeriesAdvance(
        number_of=1,
        amount=1000.0,
        label="Loan advance"
    )
    calculator.add(advance)
    profile = calculator._build_profile()
    assert len(profile) == 1
    assert profile[Column.POST_DATE.value].iloc[0].tzinfo is not None
    assert profile[Column.AMOUNT.value].iloc[0] == -1000.0

def test_build_profile_undated_payment_mode_arrear(calculator):
    """Test undated payment series with Mode.ARREAR date rolling."""
    payment = SeriesPayment(
        number_of=2,
        amount=500.0,
        frequency=Frequency.MONTHLY,
        mode=Mode.ARREAR,
        is_interest_capitalised=True,
        label="Loan repayment"
    )
    calculator.add(payment)
    profile = calculator._build_profile(pd.Timestamp("2025-01-01", tz="UTC"))
    assert len(profile) == 2
    assert profile[Column.POST_DATE.value].to_list() == [
        pd.Timestamp("2025-02-01", tz="UTC"),
        pd.Timestamp("2025-03-01", tz="UTC")
    ]
    assert (profile[Column.AMOUNT.value] == 500.0).all()
    assert (profile[Column.IS_INTEREST_CAPITALISED.value] == True).all()

def test_build_profile_undated_charge_mode_arrear(calculator):
    """Test undated charge series with Mode.ARREAR date rolling."""
    charge = SeriesCharge(
        number_of=2,
        amount=50.0,
        frequency=Frequency.MONTHLY,
        mode=Mode.ARREAR
    )
    calculator.add(charge)
    profile = calculator._build_profile(pd.Timestamp("2025-01-01", tz="UTC"))
    assert len(profile) == 2
    assert profile[Column.POST_DATE.value].to_list() == [
        pd.Timestamp("2025-02-01", tz="UTC"),
        pd.Timestamp("2025-03-01", tz="UTC")
    ]
    assert (profile[Column.AMOUNT.value] == 50.0).all()
    assert (profile[Column.IS_CHARGE.value] == True).all()

def test_build_profile_undated_charge_mode_advance(calculator):
    """Test undated charge series with Mode.ADVANCE date rolling and start_date update."""
    charge1 = SeriesCharge(
        number_of=1,
        amount=50.0,
        frequency=Frequency.MONTHLY,
        mode=Mode.ADVANCE,
        label="First fee"
    )
    charge2 = SeriesCharge(
        number_of=1,
        amount=25.0,
        frequency=Frequency.MONTHLY,
        mode=Mode.ADVANCE,
        label="Second fee"
    )
    calculator.add(charge1)
    calculator.add(charge2)
    profile = calculator._build_profile(pd.Timestamp("2025-01-01", tz="UTC"))
    assert len(profile) == 2
    assert profile[Column.POST_DATE.value].to_list() == [
        pd.Timestamp("2025-01-01", tz="UTC"),
        pd.Timestamp("2025-02-01", tz="UTC")
    ]
    assert profile[Column.AMOUNT.value].to_list() == [50.0, 25.0]
    assert (profile[Column.IS_CHARGE.value] == True).all()

def test_build_profile_undated_advances(calculator):
    advance1 = SeriesAdvance(number_of=2, frequency=Frequency.MONTHLY)
    advance2 = SeriesAdvance(number_of=1, mode=Mode.ARREAR)
    calculator._series = [advance1, advance2]
    result = calculator._build_profile(start_date)

    assert len(result) == 3
    assert result.loc[
        0, Column.POST_DATE.value
        ] == start_date  # 2026-01-01
    assert result.loc[
        1, Column.POST_DATE.value
        ] == start_date + pd.offsets.MonthBegin(1)  # 2026-02-01
    assert result.loc[
        2, Column.POST_DATE.value
        ] == start_date + pd.offsets.MonthBegin(3)  # 2026-04-01

def test_build_profile_dated_advances(calculator):
    advance1 = SeriesAdvance(number_of=2, post_date_from=start_date)
    advance2 = SeriesAdvance(
        number_of=1,
        post_date_from=date3,
        value_date_from=date3 + pd.Timedelta(days=14),
        mode=Mode.ARREAR)
    calculator._series = [advance1, advance2]
    result = calculator._build_profile(start_date)

    assert len(result) == 3
    assert result.loc[0, Column.POST_DATE.value] == start_date
    assert result.loc[1, Column.POST_DATE.value] == start_date + pd.offsets.MonthBegin(1)
    assert result.loc[2, Column.POST_DATE.value] == date3
    assert result.loc[2, Column.VALUE_DATE.value] == date3 + pd.Timedelta(days=14)
