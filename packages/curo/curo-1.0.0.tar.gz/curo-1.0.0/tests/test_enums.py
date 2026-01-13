# tests/test_enums.py
# pylint: disable=C0114, C0116
# - C0114: missing-module-docstring
# - C0116: missing-function-docstring

from curo.enums import (
    CashFlowColumn,
    CashFlowColumnExtras,
    DayCountOrigin,
    DayCountTimePeriod,
    Frequency,
    Mode,
    SortColumn,
    ValidationMode
    )

def test_frequency_values():
    assert Frequency.WEEKLY.value == "weekly"
    assert Frequency.FORTNIGHTLY.value == "fortnightly"
    assert Frequency.MONTHLY.value == "monthly"
    assert Frequency.QUARTERLY.value == "quarterly"
    assert Frequency.HALF_YEARLY.value == "half_yearly"
    assert Frequency.YEARLY.value == "yearly"
    assert len(Frequency) == 6  # Ensure all expected members are defined

def test_frequency_pandas_freq():
    assert Frequency.WEEKLY.pandas_freq == "W"
    assert Frequency.FORTNIGHTLY.pandas_freq == "2W"
    assert Frequency.MONTHLY.pandas_freq == "ME"
    assert Frequency.QUARTERLY.pandas_freq == "QE"
    assert Frequency.HALF_YEARLY.pandas_freq == "6ME"
    assert Frequency.YEARLY.pandas_freq == "YE"

def test_mode_values():
    assert Mode.ADVANCE.value == "advance"
    assert Mode.ARREAR.value == "arrear"
    assert len(Mode) == 2

def test_day_count_time_period_values():
    assert DayCountTimePeriod.DAY.value == "day"
    assert DayCountTimePeriod.WEEK.value == "week"
    assert DayCountTimePeriod.FORTNIGHT.value == "fortnight"
    assert DayCountTimePeriod.MONTH.value == "month"
    assert DayCountTimePeriod.QUARTER.value == "quarter"
    assert DayCountTimePeriod.HALF_YEAR.value == "half_year"
    assert DayCountTimePeriod.YEAR.value == "year"
    assert len(DayCountTimePeriod) == 7

def test_day_count_time_period_periods_in_year():
    assert DayCountTimePeriod.DAY.periods_in_year == 365
    assert DayCountTimePeriod.WEEK.periods_in_year == 52
    assert DayCountTimePeriod.FORTNIGHT.periods_in_year == 26
    assert DayCountTimePeriod.MONTH.periods_in_year == 12
    assert DayCountTimePeriod.QUARTER.periods_in_year == 4
    assert DayCountTimePeriod.HALF_YEAR.periods_in_year == 2
    assert DayCountTimePeriod.YEAR.periods_in_year == 1

def test_day_count_origin_values():
    assert DayCountOrigin.DRAWDOWN.value == "drawdown"
    assert DayCountOrigin.NEIGHBOUR.value == "neighbour"
    assert len(DayCountOrigin) == 2

def test_cash_flow_column_values():
    assert CashFlowColumn.POST_DATE.value == 'post_date'
    assert CashFlowColumn.VALUE_DATE.value == 'value_date'
    assert CashFlowColumn.AMOUNT.value == 'amount'
    assert CashFlowColumn.IS_KNOWN.value == 'is_known'
    assert CashFlowColumn.WEIGHTING.value == 'weighting'
    assert CashFlowColumn.LABEL.value == 'label'
    assert CashFlowColumn.MODE.value == 'mode'
    assert CashFlowColumn.IS_INTEREST_CAPITALISED.value == 'is_interest_capitalised'
    assert CashFlowColumn.IS_CHARGE.value == 'is_charge'
    assert len(CashFlowColumn) == 9

def test_cash_flow_column_extra_values():
    assert CashFlowColumnExtras.AMOUNT_DISCOUNTED.value == "amount_discounted"
    assert CashFlowColumnExtras.CAPITAL.value == "capital"
    assert CashFlowColumnExtras.CAPITAL_BALANCE.value == "capital_balance"
    assert CashFlowColumnExtras.DISCOUNT_LOG.value == "discount_log"
    assert CashFlowColumnExtras.DISCOUNTED_BALANCE.value == "discounted_balance"
    assert CashFlowColumnExtras.FACTOR.value == "factor"
    assert CashFlowColumnExtras.INTEREST.value == "interest"
    assert len(CashFlowColumnExtras) == 7

def test_sort_column_values():
    assert SortColumn.POST_DATE.value == CashFlowColumn.POST_DATE.value
    assert SortColumn.VALUE_DATE.value == CashFlowColumn.VALUE_DATE.value
    assert len(SortColumn) == 2

def test_validation_mode_values():
    assert ValidationMode.SOLVE_VALUE.value == 'solve_value'
    assert ValidationMode.SOLVE_RATE.value == 'solve_rate'
    assert len(ValidationMode) == 2
