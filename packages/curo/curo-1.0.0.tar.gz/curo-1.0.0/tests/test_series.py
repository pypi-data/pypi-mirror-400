# tests/test_series.py
# pylint: disable=C0114,C0116,C0121,W0621,
# - C0114: missing-module-docstring
# - C0116: missing-function-docstring
# = C0121: singleton-comparison
# - W0621: redefined-outer-name

import pytest
import pandas as pd
from curo.enums import CashFlowColumn as Column, Frequency, Mode
from curo.series import SeriesAdvance, SeriesPayment, SeriesCharge

@pytest.fixture
def start_date():
    return pd.Timestamp('2025-12-24', tz='UTC')  # Use UTC timezone

# SeriesAdvance Tests
def test_series_advance_defaults():
    advance = SeriesAdvance()
    assert advance.number_of == 1
    assert advance.frequency == Frequency.MONTHLY
    assert advance.label == ''
    assert advance.amount is None
    assert advance.mode == Mode.ADVANCE
    assert advance.post_date_from is None
    assert advance.value_date_from is None
    assert advance.weighting == 1.0

def test_series_advance_value_none(start_date):
    advance = SeriesAdvance(amount=None)
    assert advance.number_of == 1
    assert advance.frequency == Frequency.MONTHLY
    assert advance.amount is None
    assert advance.post_date_from is None
    assert advance.value_date_from is None

    cash_flows = advance.to_cash_flows(start_date=start_date)
    assert len(cash_flows) == 1
    assert cash_flows[Column.POST_DATE.value].iloc[0] == pd.Timestamp('2025-12-24', tz='UTC')
    assert cash_flows[Column.VALUE_DATE.value].iloc[0] == pd.Timestamp('2025-12-24', tz='UTC')
    # 'amount' assigned 0.0 placeholder value if not known (None)
    assert cash_flows[Column.AMOUNT.value].iloc[0] == 0.0
    assert not cash_flows[Column.IS_KNOWN.value].iloc[0]
    assert cash_flows[Column.WEIGHTING.value].iloc[0] == 1.0
    assert cash_flows[Column.LABEL.value].iloc[0] == ''
    assert cash_flows[Column.MODE.value].iloc[0] == Mode.ADVANCE.value
    assert cash_flows[Column.IS_INTEREST_CAPITALISED.value].iloc[0] is None

def test_series_advance_value_and_date():
    post_date = pd.Timestamp('2025-01-01', tz='UTC')
    advance = SeriesAdvance(amount=1000.0, post_date_from=post_date)
    assert advance.number_of == 1
    assert advance.frequency == Frequency.MONTHLY
    assert advance.amount == 1000.0
    assert advance.post_date_from == post_date
    assert advance.value_date_from == post_date
    assert advance.mode == Mode.ADVANCE
    assert advance.weighting == 1.0

    cash_flows = advance.to_cash_flows(start_date=pd.Timestamp('2025-12-24', tz='UTC'))
    assert len(cash_flows) == 1
    assert cash_flows[Column.POST_DATE.value].iloc[0] == post_date
    assert cash_flows[Column.VALUE_DATE.value].iloc[0] == post_date
    assert cash_flows[Column.AMOUNT.value].iloc[0] == 1000.0
    assert cash_flows[Column.IS_KNOWN.value].iloc[0]
    assert cash_flows[Column.WEIGHTING.value].iloc[0] == 1.0
    assert cash_flows[Column.LABEL.value].iloc[0] == ''
    assert cash_flows[Column.MODE.value].iloc[0] == Mode.ADVANCE.value
    assert cash_flows[Column.IS_INTEREST_CAPITALISED.value].iloc[0] is None

def test_series_advance_full_spec():
    post_date = pd.Timestamp('2025-01-01', tz='UTC')
    value_date = pd.Timestamp('2025-01-31', tz='UTC')
    advance = SeriesAdvance(
        number_of=3,
        frequency=Frequency.QUARTERLY,
        label='Loan Advance',
        amount=5000.0,
        post_date_from=post_date,
        value_date_from=value_date,
        mode=Mode.ARREAR,
        weighting=2.0
    )
    assert advance.number_of == 3
    assert advance.frequency == Frequency.QUARTERLY
    assert advance.label == 'Loan Advance'
    assert advance.amount == 5000.0
    assert advance.post_date_from == post_date
    assert advance.value_date_from == value_date
    assert advance.mode == Mode.ARREAR
    assert advance.weighting == 2.0

    cash_flows = advance.to_cash_flows(start_date=pd.Timestamp('2025-12-24', tz='UTC'))
    assert len(cash_flows) == 3
    expected_dates = [
        pd.Timestamp('2025-01-01', tz='UTC'),
        pd.Timestamp('2025-04-01', tz='UTC'),
        pd.Timestamp('2025-07-01', tz='UTC')
    ]
    expected_value_dates = [
        pd.Timestamp('2025-01-31', tz='UTC'),
        pd.Timestamp('2025-04-30', tz='UTC'),
        pd.Timestamp('2025-07-31', tz='UTC')
    ]
    pd.testing.assert_series_equal(
        cash_flows[Column.POST_DATE.value],
        pd.Series(expected_dates, name=Column.POST_DATE.value)
    )
    pd.testing.assert_series_equal(
        cash_flows[Column.VALUE_DATE.value],
        pd.Series(expected_value_dates, name=Column.VALUE_DATE.value)
    )
    assert (cash_flows[Column.AMOUNT.value] == 5000.0).all()
    assert (cash_flows[Column.IS_KNOWN.value]).all()
    assert (cash_flows[Column.WEIGHTING.value] == 2.0).all()
    assert (cash_flows[Column.LABEL.value] == 'Loan Advance').all()
    assert (cash_flows[Column.MODE.value] == Mode.ARREAR.value).all()
    assert (cash_flows[Column.IS_INTEREST_CAPITALISED.value].isna()).all()

def test_series_advance_validation_errors():
    with pytest.raises(ValueError, match="number_of must be >= 1"):
        SeriesAdvance(number_of=0)
    with pytest.raises(ValueError, match="weighting must be > 0"):
        SeriesAdvance(weighting=0.0)
    with pytest.raises(ValueError, match="post_date_from required when value_date_from is set"):
        SeriesAdvance(value_date_from=pd.Timestamp('2025-01-01', tz='UTC'))
    with pytest.raises(ValueError, match="value_date_from must be on or after post_date_from"):
        SeriesAdvance(
            post_date_from=pd.Timestamp('2025-01-02', tz='UTC'),
            value_date_from=pd.Timestamp('2025-01-01', tz='UTC')
        )

# SeriesPayment Tests
def test_series_payment_defaults():
    payment = SeriesPayment()
    assert payment.number_of == 1
    assert payment.frequency == Frequency.MONTHLY
    assert payment.label == ''
    assert payment.amount is None
    assert payment.mode == Mode.ADVANCE
    assert payment.post_date_from is None
    assert payment.value_date_from is None
    assert payment.weighting == 1.0
    assert payment.is_interest_capitalised is True

def test_series_payment_value_none(start_date):
    payment = SeriesPayment(amount=None, is_interest_capitalised=False)
    assert payment.number_of == 1
    assert payment.frequency == Frequency.MONTHLY
    assert payment.amount is None
    assert payment.post_date_from is None
    assert payment.value_date_from is None
    assert payment.is_interest_capitalised is False

    cash_flows = payment.to_cash_flows(start_date=start_date)
    assert len(cash_flows) == 1
    assert cash_flows[Column.POST_DATE.value].iloc[0] == pd.Timestamp('2025-12-24', tz='UTC')
    assert cash_flows[Column.VALUE_DATE.value].iloc[0] == pd.Timestamp('2025-12-24', tz='UTC')
    # 'amount' assigned 0.0 placeholder value if not known (None)
    assert cash_flows[Column.AMOUNT.value].iloc[0] == 0.0
    assert not cash_flows[Column.IS_KNOWN.value].iloc[0]
    assert cash_flows[Column.WEIGHTING.value].iloc[0] == 1.0
    assert cash_flows[Column.LABEL.value].iloc[0] == ''
    assert cash_flows[Column.MODE.value].iloc[0] == Mode.ADVANCE.value
    assert not cash_flows[Column.IS_INTEREST_CAPITALISED.value].iloc[0] # false

def test_series_payment_value_and_date():
    post_date = pd.Timestamp('2025-01-01', tz='UTC')
    payment = SeriesPayment(amount=500.0, post_date_from=post_date, is_interest_capitalised=True)
    assert payment.number_of == 1
    assert payment.frequency == Frequency.MONTHLY
    assert payment.amount == 500.0
    assert payment.post_date_from == post_date
    assert payment.value_date_from == post_date
    assert payment.mode == Mode.ADVANCE
    assert payment.weighting == 1.0
    assert payment.is_interest_capitalised is True

    cash_flows = payment.to_cash_flows(start_date=pd.Timestamp('2025-12-24', tz='UTC'))
    assert len(cash_flows) == 1
    assert cash_flows[Column.POST_DATE.value].iloc[0] == post_date
    assert cash_flows[Column.VALUE_DATE.value].iloc[0] == post_date
    assert cash_flows[Column.AMOUNT.value].iloc[0] == 500.0
    assert cash_flows[Column.IS_KNOWN.value].iloc[0]
    assert cash_flows[Column.WEIGHTING.value].iloc[0] == 1.0
    assert cash_flows[Column.LABEL.value].iloc[0] == ''
    assert cash_flows[Column.MODE.value].iloc[0] == Mode.ADVANCE.value
    assert cash_flows[Column.IS_INTEREST_CAPITALISED.value].iloc[0] # true

def test_series_payment_full_spec():
    post_date = pd.Timestamp('2025-01-31', tz='UTC')
    payment = SeriesPayment(
        number_of=3,
        frequency=Frequency.QUARTERLY,
        label='Rental',
        amount=1000.0,
        post_date_from=post_date,
        #value_date_from= not allowed to be set
        mode=Mode.ARREAR,
        weighting=1.5,
        is_interest_capitalised=False
    )
    assert payment.number_of == 3
    assert payment.frequency == Frequency.QUARTERLY
    assert payment.label == 'Rental'
    assert payment.amount == 1000.0
    assert payment.post_date_from == post_date
    assert payment.value_date_from == post_date
    assert payment.mode == Mode.ARREAR
    assert payment.weighting == 1.5
    assert payment.is_interest_capitalised is False

    cash_flows = payment.to_cash_flows(start_date=pd.Timestamp('2025-12-24', tz='UTC'))
    assert len(cash_flows) == 3
    expected_dates = [
        pd.Timestamp('2025-01-31', tz='UTC'),
        pd.Timestamp('2025-04-30', tz='UTC'),
        pd.Timestamp('2025-07-31', tz='UTC')
    ]
    expected_value_dates = [
        pd.Timestamp('2025-01-31', tz='UTC'),
        pd.Timestamp('2025-04-30', tz='UTC'),
        pd.Timestamp('2025-07-31', tz='UTC')
    ]
    pd.testing.assert_series_equal(
        cash_flows[Column.POST_DATE.value],
        pd.Series(expected_dates, name=Column.POST_DATE.value)
    )
    pd.testing.assert_series_equal(
        cash_flows[Column.VALUE_DATE.value],
        pd.Series(expected_value_dates, name=Column.VALUE_DATE.value)
    )
    assert (cash_flows[Column.AMOUNT.value] == 1000.0).all()
    assert (cash_flows[Column.IS_KNOWN.value]).all()
    assert (cash_flows[Column.WEIGHTING.value] == 1.5).all()
    assert (cash_flows[Column.LABEL.value] == 'Rental').all()
    assert (cash_flows[Column.MODE.value] == Mode.ARREAR.value).all()
    assert (cash_flows[Column.IS_INTEREST_CAPITALISED.value] == False).all()
    #assert (not cash_flows[Column.IS_INTEREST_CAPITALISED.value]).all() # false

def test_series_payment_validation_errors():
    with pytest.raises(ValueError, match="number_of must be >= 1"):
        SeriesPayment(number_of=0)
    with pytest.raises(ValueError, match="weighting must be > 0"):
        SeriesPayment(weighting=0.0)
    with pytest.raises(ValueError, match="value_date_from must not be defined for SeriesPayment"):
        SeriesPayment(
            post_date_from=pd.Timestamp('2025-01-02', tz='UTC'),
            value_date_from=pd.Timestamp('2025-01-01', tz='UTC')
        )

# SeriesCharge Tests
def test_series_charge_defaults():
    charge = SeriesCharge(amount=50.0)
    assert charge.number_of == 1
    assert charge.frequency == Frequency.MONTHLY
    assert charge.label == ''
    assert charge.amount == 50.0
    assert charge.mode == Mode.ADVANCE
    assert charge.post_date_from is None
    assert charge.value_date_from is None
    assert charge.weighting == 1.0

def test_series_charge_value_required(start_date):
    charge = SeriesCharge(amount=75.0)
    assert charge.number_of == 1
    assert charge.frequency == Frequency.MONTHLY
    assert charge.amount == 75.0
    assert charge.post_date_from is None
    assert charge.value_date_from is None

    cash_flows = charge.to_cash_flows(start_date=start_date)
    assert len(cash_flows) == 1
    assert cash_flows[Column.POST_DATE.value].iloc[0] == pd.Timestamp('2025-12-24', tz='UTC')
    assert cash_flows[Column.VALUE_DATE.value].iloc[0] == pd.Timestamp('2025-12-24', tz='UTC')
    assert cash_flows[Column.AMOUNT.value].iloc[0] == 75.0
    assert cash_flows[Column.IS_KNOWN.value].iloc[0]
    assert cash_flows[Column.WEIGHTING.value].iloc[0] == 1.0
    assert cash_flows[Column.LABEL.value].iloc[0] == ''
    assert cash_flows[Column.MODE.value].iloc[0] == Mode.ADVANCE.value
    assert cash_flows[Column.IS_INTEREST_CAPITALISED.value].iloc[0] is None

def test_series_charge_full_spec():
    post_date = pd.Timestamp('2025-01-01', tz='UTC')
    charge = SeriesCharge(
        number_of=2,
        frequency=Frequency.MONTHLY,
        label='Arrangement Fee',
        amount=100.0,
        post_date_from=post_date,
        mode=Mode.ARREAR,
        weighting=1.0
    )
    assert charge.number_of == 2
    assert charge.frequency == Frequency.MONTHLY
    assert charge.label == 'Arrangement Fee'
    assert charge.amount == 100.0
    assert charge.post_date_from == post_date
    assert charge.value_date_from == post_date  # Set by Series.__post_init__
    assert charge.mode == Mode.ARREAR
    assert charge.weighting == 1.0

    cash_flows = charge.to_cash_flows(start_date=pd.Timestamp('2025-12-24', tz='UTC'))
    assert len(cash_flows) == 2
    expected_dates = [
        pd.Timestamp('2025-01-01', tz='UTC'),
        pd.Timestamp('2025-02-01', tz='UTC')
    ]
    expected_value_dates = [
        pd.Timestamp('2025-01-01', tz='UTC'),
        pd.Timestamp('2025-02-01', tz='UTC')
    ]
    pd.testing.assert_series_equal(
        cash_flows[Column.POST_DATE.value],
        pd.Series(expected_dates, name=Column.POST_DATE.value)
    )
    pd.testing.assert_series_equal(
        cash_flows[Column.VALUE_DATE.value],
        pd.Series(expected_value_dates, name=Column.VALUE_DATE.value)
    )
    assert (cash_flows[Column.AMOUNT.value] == 100.0).all()
    assert (cash_flows[Column.IS_KNOWN.value]).all()
    assert (cash_flows[Column.WEIGHTING.value] == 1.0).all()
    assert (cash_flows[Column.LABEL.value] == 'Arrangement Fee').all()
    assert (cash_flows[Column.MODE.value] == Mode.ARREAR.value).all()
    assert (cash_flows[Column.IS_INTEREST_CAPITALISED.value].isna()).all()

def test_series_charge_validation_errors():
    with pytest.raises(ValueError, match="number_of must be >= 1"):
        SeriesCharge(number_of=0, amount=50.0)
    with pytest.raises(ValueError, match="weighting must be > 0"):
        SeriesCharge(weighting=0.0, amount=50.0)
    with pytest.raises(ValueError, match="amount is required for SeriesCharge"):
        SeriesCharge(amount=None)
    with pytest.raises(ValueError, match="value_date_from must not be defined for SeriesCharge"):
        SeriesCharge(amount=50.0, value_date_from=pd.Timestamp('2025-01-01', tz='UTC'))
