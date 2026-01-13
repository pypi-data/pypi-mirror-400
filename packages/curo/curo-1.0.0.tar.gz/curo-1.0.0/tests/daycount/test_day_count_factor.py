# tests/daycount/test_day_count_factor.py
# pylint: disable=C0114, C0116, W0621
# - C0114: missing-module-docstring
# - C0116: missing-function-docstring
# - W0621: redefined-outer-name

import pytest
from curo.daycount.day_count_factor import DayCountFactor

def test_day_count_factor_init_standard():
    factor = DayCountFactor(
        primary_period_fraction=31/360,
        discount_factor_log=["31/360"]
    )
    assert factor.primary_period_fraction == 31/360
    assert factor.discount_factor_log == ["31/360"]
    assert factor.partial_period_fraction is None
    assert factor.discount_terms_log == []
    assert str(factor) == "f = 31/360 = 0.08611111"
    assert factor.to_folded_string() == "f = 31/360 = 0.08611111"

def test_day_count_factor_init_us_appendix_j():
    factor = DayCountFactor(
        primary_period_fraction=1.0,
        partial_period_fraction=5/30,
        discount_terms_log=["t = 1", "f = 5/30 = 0.16666667","p = 365"]
    )
    assert factor.primary_period_fraction == 1.0
    assert factor.partial_period_fraction == 5/30
    assert factor.discount_terms_log == ["t = 1", "f = 5/30 = 0.16666667","p = 365"]
    assert str(factor) == "t = 1 : f = 5/30 = 0.16666667 : p = 365"
    assert factor.to_folded_string() == "t = 1 : f = 5/30 = 0.16666667 : p = 365"

def test_operands_to_string_fraction():
    assert DayCountFactor.operands_to_string(31, 360) == "31/360"
    assert DayCountFactor.operands_to_string(5, 30) == "5/30"

def test_operands_to_string_whole():
    assert DayCountFactor.operands_to_string(365, 365) == "1"
    assert DayCountFactor.operands_to_string(730, 365) == "2"

def test_operands_to_string_mixed():
    assert DayCountFactor.operands_to_string(370, 365) == "1 + 5/365"
    assert DayCountFactor.operands_to_string(35, 30) == "1 + 5/30"

def test_operands_to_string_zero_denominator():
    assert DayCountFactor.operands_to_string(5, 0) == "5"

def test_str_standard():
    factor = DayCountFactor(
        primary_period_fraction=31/360,
        discount_factor_log=["31/360"]
    )
    assert factor.partial_period_fraction is None
    assert factor.discount_terms_log == []
    assert str(factor) == "f = 31/360 = 0.08611111"
    assert factor.to_folded_string() == "f = 31/360 = 0.08611111"

def test_str_us_appendix_j():
    factor = DayCountFactor(
        primary_period_fraction=1,
        partial_period_fraction=5/30,
        discount_terms_log=["t = 1","f = 5/30 = 0.16666667", "p = 12"]
    )
    assert str(factor) == "t = 1 : f = 5/30 = 0.16666667 : p = 12"
    assert factor.to_folded_string() == "t = 1 : f = 5/30 = 0.16666667 : p = 12"

def test_str_empty_operands():
    factor = DayCountFactor(
        primary_period_fraction=0.0,
        partial_period_fraction=0.0,
        discount_factor_log=[],
        discount_terms_log=[]
    )
    assert str(factor) == "0"

def test_str_mixed_operands():
    with pytest.raises(
        ValueError,
        match="Mix of discount terms and discount factor log entries not supported"):
        factor = DayCountFactor(
            primary_period_fraction=0.0,
            partial_period_fraction=0.0,
            discount_factor_log=["1"],
            discount_terms_log=["2"]
        )
        str(factor)

def test_folded_str_mixed_operands():
    with pytest.raises(
        ValueError,
        match="Mix of discount terms and discount factor log entries not supported"):
        factor = DayCountFactor(
            primary_period_fraction=0.0,
            partial_period_fraction=0.0,
            discount_factor_log=["1"],
            discount_terms_log=["2"]
        )
        factor.to_folded_string()

def test_folded_str_zero_denominator():
    with pytest.raises(
        ValueError,
        match="Invalid operand format: 1/0"): #Zero denominator in operand"):
        factor = DayCountFactor(
            primary_period_fraction=0.0,
            partial_period_fraction=0.0,
            discount_factor_log=["1/0"],
            discount_terms_log=None
        )
        factor.to_folded_string()

def test_str_fractional_operands():
    factor = DayCountFactor(
        primary_period_fraction=0.0,
        partial_period_fraction=1.0,
        discount_factor_log=None,
        discount_terms_log=["1.0"]
    )
    assert str(factor) == "1.0"
    assert factor.to_folded_string() == "1.0"

def test_to_folded_fractional_operands():
    factor = DayCountFactor(
        primary_period_fraction=0.0,
        partial_period_fraction=None,
        discount_factor_log=None,
        discount_terms_log=["0.0"]
    )
    assert str(factor) == "0.0"
    assert factor.to_folded_string() == "0.0"

def test_to_folded_string_standard():
    factor = DayCountFactor(
        primary_period_fraction=2.36388889,
        discount_factor_log=["100/360", "365/365", "365/365", "31/360"]
    )
    assert factor.to_folded_string() == "f = 100/360 + 2 + 31/360 = 2.36388889"

def test_to_folded_string_composite():
    factor = DayCountFactor(
        primary_period_fraction=1.08333333,
        discount_factor_log=["1 + 1/12"]
    )
    assert factor.to_folded_string() == "f = 1 + 1/12 = 1.08333333"

def test_to_folded_string_us_appendix_j():
    factor = DayCountFactor(
        primary_period_fraction=2.0,
        partial_period_fraction=5/30,
        discount_terms_log=["t = 2","f = 5/30 = 0.16666667", "p = 12"],
        discount_factor_log=[]
    )
    assert factor.to_folded_string() == "t = 2 : f = 5/30 = 0.16666667 : p = 12"

# Additional tests from Dart
def test_str_and_folded_string_2_365_two_ones_31_365():
    factor = DayCountFactor(
        primary_period_fraction=2.09041096,
        discount_factor_log=["2/365", "1", "1", "31/365"]
    )
    assert str(factor) == "f = 2/365 + 1 + 1 + 31/365 = 2.09041096"
    assert factor.to_folded_string() == "f = 2/365 + 2 + 31/365 = 2.09041096"

def test_str_and_folded_string_2_366_two_ones_31_365():
    factor = DayCountFactor(
        primary_period_fraction=2.09039599,
        discount_factor_log=["2/366", "1", "1", "31/365"]
    )
    assert str(factor) == "f = 2/366 + 1 + 1 + 31/365 = 2.09039599"
    assert factor.to_folded_string() == "f = 2/366 + 2 + 31/365 = 2.09039599"

def test_str_and_folded_string_2_366_three_ones():
    factor = DayCountFactor(
        primary_period_fraction=3.00546448,
        discount_factor_log=["2/366", "1", "1", "1"]
    )
    assert str(factor) == "f = 2/366 + 1 + 1 + 1 = 3.00546448"
    assert factor.to_folded_string() == "f = 2/366 + 3 = 3.00546448"

def test_str_and_folded_string_four_ones():
    factor = DayCountFactor(
        primary_period_fraction=4.0,
        discount_factor_log=["1", "1", "1", "1"]
    )
    assert str(factor) == "f = 1 + 1 + 1 + 1 = 4.00000000"
    assert factor.to_folded_string() == "f = 4 = 4.00000000"

def test_init_negative_fractions():
    with pytest.raises(ValueError, match="primary_period_fraction cannot be negative"):
        DayCountFactor(primary_period_fraction=-0.1, discount_factor_log=["-1/360"])
    with pytest.raises(ValueError, match="partial_period_fraction cannot be negative"):
        DayCountFactor(
            primary_period_fraction=1.0,
            partial_period_fraction=-0.1,
            discount_terms_log=["t = 1", "f = -1/30", "p = 12"]
        )

def test_to_folded_string_precomputed_operands():
    # Test that to_folded_string correctly strips pre-computed results
    factor = DayCountFactor(
        primary_period_fraction=31/360,
        discount_factor_log=["31/360 = 0.08611111"]
    )
    assert factor.to_folded_string() == "f = 31/360 = 0.08611111"
    assert str(factor) == "f = 31/360 = 0.08611111"

def test_malformed_operands():
    factor = DayCountFactor(
        primary_period_fraction=0.0,
        discount_factor_log=["invalid/360"]
    )
    with pytest.raises(ValueError, match="Invalid operand format"):
        factor.to_folded_string()
    factor = DayCountFactor(
        primary_period_fraction=0.0,
        discount_terms_log=["t = invalid"]
    )
    assert str(factor) == "t = invalid"  # No error, but verify output

def test_empty_discount_factor_log_non_zero_fraction():
    factor = DayCountFactor(
        primary_period_fraction=0.5,
        discount_factor_log=[]
    )
    assert str(factor) == "0"
    assert factor.to_folded_string() == "0"

def test_operands_to_string_edge_cases():
    assert DayCountFactor.operands_to_string(1000000, 365) == "2739 + 265/365"

def test_partial_discount_terms_log():
    factor = DayCountFactor(
        primary_period_fraction=1.0,
        partial_period_fraction=None,
        discount_terms_log=["t = 1"]
    )
    assert str(factor) == "t = 1"
    assert factor.to_folded_string() == "t = 1"
    factor = DayCountFactor(
        primary_period_fraction=0.0,
        partial_period_fraction=5/30,
        discount_terms_log=["f = 5/30 = 0.16666667", "p = 12"]
    )
    assert str(factor) == "f = 5/30 = 0.16666667 : p = 12"
    assert factor.to_folded_string() == "f = 5/30 = 0.16666667 : p = 12"
