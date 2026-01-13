# test_calculator_sort_cash_flows.py
# pylint: disable=C0114,C0116,W0212,W0621
# - C0114: missing-module-docstring
# - C0116: missing-function-docstring
# - W0212: protected-access
# - W0621: redefined-outer-name

import pytest
import pandas as pd
from curo.calculator import Calculator
from curo.enums import CashFlowColumn as Column, SortColumn
from curo.exceptions import ValidationError

@pytest.fixture
def calculator():
    return Calculator(precision=2)

@pytest.fixture
def unsorted_profile():
    return pd.DataFrame({
        Column.POST_DATE.value: [
            pd.Timestamp("2025-01-01", tz="UTC"),
            pd.Timestamp("2025-01-01", tz="UTC"),
            pd.Timestamp("2025-01-01", tz="UTC"),
            pd.Timestamp("2025-02-01", tz="UTC")
        ],
        Column.VALUE_DATE.value: [
            pd.Timestamp("2025-01-01", tz="UTC"),
            pd.Timestamp("2025-01-01", tz="UTC"),
            pd.Timestamp("2025-01-01", tz="UTC"),
            pd.Timestamp("2025-02-01", tz="UTC")
        ],
        Column.AMOUNT.value: [1000.0, 500.0, 50.0, 200.0],
        Column.IS_KNOWN.value: [True, True, True, True],
        Column.WEIGHTING.value: [1.0, 1.0, 1.0, 1.0],
        Column.LABEL.value: ["Advance", "Payment", "Charge", "Advance"],
        Column.MODE.value: ["advance", "advance", "advance", "advance"],
        Column.IS_INTEREST_CAPITALISED.value: [None, True, None, None],
        Column.IS_CHARGE.value: [False, False, True, False]
    })

def test_sort_cash_flows_empty(calculator):
    """Test sorting an empty DataFrame."""
    empty_df = pd.DataFrame(columns=[col.value for col in Column])
    sorted_df = calculator._sort_cash_flows(empty_df)
    assert sorted_df.empty
    assert sorted_df.columns.tolist() == empty_df.columns.tolist()

def test_sort_cash_flows_by_post_date(calculator, unsorted_profile):
    """Test sorting by post_date with object type and amount."""
    sorted_df = calculator._sort_cash_flows(unsorted_profile, sort_by=SortColumn.POST_DATE)
    expected_post_dates = [
        pd.Timestamp("2025-01-01", tz="UTC"),
        pd.Timestamp("2025-01-01", tz="UTC"),
        pd.Timestamp("2025-01-01", tz="UTC"),
        pd.Timestamp("2025-02-01", tz="UTC")
    ]
    expected_labels = ["Advance", "Payment", "Charge", "Advance"]
    expected_amounts = [1000.0, 500.0, 50.0, 200.0]
    assert sorted_df[Column.POST_DATE.value].tolist() == expected_post_dates
    assert sorted_df[Column.LABEL.value].tolist() == expected_labels
    assert sorted_df[Column.AMOUNT.value].tolist() == expected_amounts

def test_sort_cash_flows_by_value_date(calculator, unsorted_profile):
    """Test sorting by value_date with object type."""
    unsorted_profile[Column.VALUE_DATE.value] = [
        pd.Timestamp("2025-01-02", tz="UTC"),
        pd.Timestamp("2025-01-01", tz="UTC"),
        pd.Timestamp("2025-01-01", tz="UTC"),
        pd.Timestamp("2025-02-01", tz="UTC")
    ]
    sorted_df = calculator._sort_cash_flows(unsorted_profile, sort_by=SortColumn.VALUE_DATE)
    expected_labels = ["Payment", "Charge", "Advance", "Advance"]
    assert sorted_df[Column.LABEL.value].tolist() == expected_labels

def test_sort_cash_flows_no_amount_sort_unknown(calculator, unsorted_profile):
    """Test skipping amount sort when is_known=False."""
    unsorted_profile[Column.IS_KNOWN.value] = [True, False, True, True]
    sorted_df = calculator._sort_cash_flows(unsorted_profile, sort_by=SortColumn.POST_DATE)
    expected_labels = ["Advance", "Payment", "Charge", "Advance"]
    assert sorted_df[Column.LABEL.value].tolist() == expected_labels

def test_sort_cash_flows_invalid_sort_by(calculator, unsorted_profile):
    """Test invalid sort_by raises ValidationError."""
    with pytest.raises(ValidationError, match="sort_by must be a SortColumn value"):
        calculator._sort_cash_flows(unsorted_profile, sort_by="invalid")
