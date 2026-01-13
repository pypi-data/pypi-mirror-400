"""
Defines the DayCountFactor class for day count convention results.
"""
from typing import List, Optional
from curo.utils import gauss_round

class DayCountFactor:
    """
    Represents the result of a day count convention calculation for financial discount formulas.

    Stores the primary year fraction (`t`) used in all conventions, and for US Appendix J, an
    optional fractional period (`f`). Includes operand logs for calculation proofs, such as
    demonstrating APR or XIRR derivations. Supports discount formulas:
    - Non-US Appendix J: `d = a × (1 + i)^(-t)`
    - US Appendix J: `d = a / ((1 + f * i / p) * (1 + i / p)^t)`

    Attributes:
        primary_period_fraction (float): The primary year fraction (`t`) for all conventions.
        partial_period_fraction (Optional[float]): The fractional period (`f`) for US Appendix J.
        discount_factor_log (List[str]): List of discount factor strings for non-US Appendix J
            conventions (e.g., ["31/360 = 0.08611111"]).
        discount_terms_log (List[str]): List of discount term strings for US Appendix J
            (e.g., ["t = 1", "f = 5/30 = 0.16666667", "p = 12"]).

    Note:
        Only one of `discount_factor_log` or `discount_terms_log` should be non-empty, as they
        correspond to mutually exclusive convention types.

    Examples:
        >>> factor = DayCountFactor(
        ...     primary_period_fraction=0.08611111,
        ...     discount_factor_log=["31/360 = 0.08611111"]
        ... )
        >>> print(factor)
        f = 31/360 = 0.08611111
        >>> us_factor = DayCountFactor(
        ...     primary_period_fraction=1.0,
        ...     partial_period_fraction=0.16666667,
        ...     discount_terms_log=["t = 1", "f = 5/30 = 0.16666667", "p = 12"]
        ... )
        >>> print(us_factor)
        t = 1 : f = 5/30 = 0.16666667 : p = 12
    """
    def __init__(
        self,
        primary_period_fraction: float,
        partial_period_fraction: Optional[float] = None,
        discount_factor_log: Optional[List[str]] = None,
        discount_terms_log: Optional[List[str]] = None
    ):
        """
        Initialize a DayCountFactor for day count convention results.

        Args:
            primary_period_fraction (float): The primary year fraction (`t`) for all conventions.
            partial_period_fraction (Optional[float]): The fractional period (`f`) for
                US Appendix J.
            discount_factor_log (Optional[List[str]]): List of discount factor strings for non-US
                Appendix J conventions (e.g., ["31/360 = 0.08611111"]).
            discount_terms_log (Optional[List[str]]): List of discount term strings for
                US Appendix J (e.g., ["t = 1", "f = 5/30 = 0.16666667", "p = 12"]).

        Raises:
            ValueError: If `primary_period_fraction` or `partial_period_fraction` (if provided)
                is negative.
        """
        if primary_period_fraction < 0:
            raise ValueError("primary_period_fraction cannot be negative")
        if partial_period_fraction is not None and partial_period_fraction < 0:
            raise ValueError("partial_period_fraction cannot be negative")
        self.primary_period_fraction = primary_period_fraction
        self.partial_period_fraction = partial_period_fraction
        self.discount_factor_log = [] if discount_factor_log is None else discount_factor_log
        self.discount_terms_log = [] if discount_terms_log is None else discount_terms_log

    @staticmethod
    def operands_to_string(numerator: int, denominator: int) -> str:
        """
        Formats operands as a string, representing whole periods and fractions.

        Used for calculation proofs, showing how year fractions are derived for
        non-US Appendix J conventions or components of US Appendix J terms.

        Args:
            numerator (int): Days, weeks, months, or years between two dates.
            denominator (int): Corresponding periods in a year (e.g., 360, 365).

        Returns:
            str: Formatted string, e.g., "31/360", "2", or "1 + 5/365".

        Examples:
            >>> DayCountFactor.operands_to_string(31, 360)
            '31/360'
            >>> DayCountFactor.operands_to_string(730, 365)
            '2'
            >>> DayCountFactor.operands_to_string(370, 365)
            '1 + 5/365'
        """
        if denominator == 0:
            return str(numerator)
        whole_period = numerator // denominator
        remainder = numerator % denominator
        if whole_period == 0 and remainder != 0:
            return f"{remainder}/{denominator}"
        if remainder == 0:
            return str(whole_period)
        return f"{whole_period} + {remainder}/{denominator}"

    def __str__(self) -> str:
        """
        Returns a string representation of the factor equation, rounded to 8 decimals.

        For non-US Appendix J conventions, shows operands and year fraction from
        `discount_factor_log`, e.g., "31/360 = 0.08611111". For US Appendix J, shows
        terms from `discount_terms_log`, e.g., "t = 1 : f = 5/30 = 0.16666667 : p = 12".

        Returns:
            str: Formatted factor equation, or "0" if no log entries are present.

        Raises:
            ValueError: If both `discount_factor_log` and `discount_terms_log`
                are non-empty.
        """
        if self.discount_terms_log and self.discount_factor_log:
            raise ValueError(
                "Mix of discount terms and discount factor log entries not supported")
        if not self.discount_terms_log and not self.discount_factor_log:
            return "0"
        if self.discount_terms_log:
            return " : ".join(self.discount_terms_log)

        # Strip pre-computed results from discount_factor_log
        cleaned_operands = [operand.split(" = ")[0].strip() for operand in self.discount_factor_log]
        discount_factor = " + ".join(cleaned_operands)
        return f"f = {discount_factor} = {gauss_round(self.primary_period_fraction, 8):.8f}"

    def to_folded_string(self) -> str:
        """
        Returns a compressed string representation of the factor equation, rounded to 8 decimals.

        For non-US Appendix J conventions, folds identical operands in `discount_factor_log` (e.g.,
        "365/365 + 365/365" becomes "2") and simplifies whole-number fractions (e.g., "365/365"
        becomes "1"). For US Appendix J, returns `discount_terms_log` unchanged, as terms do not
        require folding.

        Returns:
            str: Compressed factor equation, e.g., "100/360 + 1 + 31/360 = 2.36388889" for non-US
                Appendix J, or "t = 1 : f = 5/30 = 0.16666667 : p = 12" for US Appendix J, or "0"
                if no log entries are present.

        Raises:
            ValueError: If both `discount_factor_log` and `discount_terms_log` are non-empty.

        Examples:
            >>> factor = DayCountFactor(
            ...     primary_period_fraction=1.08333333,
            ...     discount_factor_log=["1 + 1/12 = 1.08333333"]
            ... )
            >>> factor.to_folded_string()
            'f = 1 + 1/12 = 1.08333333'
        """
        if self.discount_terms_log and self.discount_factor_log:
            raise ValueError(
                "Mix of discount terms and discount factor log entries not supported")
        if not self.discount_terms_log and not self.discount_factor_log:
            return "0"
        if self.discount_terms_log:
            return " : ".join(self.discount_terms_log)
        discount_terms = []
        if self.discount_factor_log:
            operand_counts = {}
            for operand in self.discount_factor_log:
                # Strip any pre-computed result (e.g., "31/360 = 0.08611111" -> "31/360")
                operand = operand.split(" = ")[0].strip()
                parts = [part.strip() for part in operand.split(" + ")]
                simplified_parts = []
                for part in parts:
                    if "/" in part:
                        try:
                            num, denom = map(int, part.split("/"))
                            if denom == 0:
                                raise ValueError("Zero denominator in operand")
                        except ValueError as e:
                            raise ValueError(f"Invalid operand format: {part}") from e
                        simplified_parts.append(self.operands_to_string(num, denom))
                    else:
                        simplified_parts.append(part)
                simplified_operand = " + ".join(simplified_parts)
                operand_counts[simplified_operand] = operand_counts.get(simplified_operand, 0) + 1
            for operand, count in operand_counts.items():
                discount_terms.append(f"{count}" if count > 1 else operand)
        primary_period_terms = [" + ".join(discount_terms)]
        # pylint: disable=C0301:line-too-long
        return f"f = {' '.join(primary_period_terms)} = {gauss_round(self.primary_period_fraction, 8):.8f}"
           