"""
Implements the Actual/360 day count convention.
"""

import pandas as pd
from curo.daycount.convention import Convention
from curo.daycount.day_count_factor import DayCountFactor

class Actual360(Convention):
    """
    Implements the Actual/360 day count convention.

    Counts the actual number of days between two dates, excluding the end date, and
    divides by 360 to compute the year fraction. Suitable for compound interest
    calculations and XIRR when `use_xirr_method` is True.

    Args:
        use_post_dates: If True, uses cash flow post dates for day counts; if False, uses
            value dates. Defaults to True.
        include_non_financing_flows: If True, includes non-financing cash flows (e.g., fees)
            in factor computations; if False, excludes them. Defaults to False.
        use_xirr_method: If True, uses the XIRR method, setting day count origin to
            DRAWDOWN; if False, uses NEIGHBOUR. Defaults to False.

    Examples:
        >>> dc = Actual360()
        >>> factor = dc.compute_factor(
        ...     pd.Timestamp('2020-01-28', tz='UTC'),
        ...     pd.Timestamp('2020-02-28', tz='UTC')
        ... )
        >>> print(factor)
        f = 31/360 = 0.08611111
    """
    def __init__(
        self,
        use_post_dates: bool = True,
        include_non_financing_flows: bool = False,
        use_xirr_method: bool = False
    ):
        super().__init__(
            use_post_dates=use_post_dates,
            include_non_financing_flows=include_non_financing_flows,
            use_xirr_method=use_xirr_method
        )

    def compute_factor(self, start: pd.Timestamp, end: pd.Timestamp) -> DayCountFactor:
        """
        Computes the year fraction between two dates using Actual/360.

        Args:
            start: The earlier date (pd.Timestamp).
            end: The later date (pd.Timestamp).

        Returns:
            DayCountFactor: The year fraction (days / 360) with operand log.

        Raises:
            ValueError: If `end` is before `start`.

        Examples:
            >>> dc = Actual360()
            >>> factor = dc.compute_factor(
            ...     pd.Timestamp('2020-01-28', tz='UTC'),
            ...     pd.Timestamp('2020-02-28', tz='UTC')
            ... )
            >>> factor.primary_period_fraction 
            0.08611111111111111
            >>> factor.discount_factor_log
            ['31/360']
        """
        if end < start:
            raise ValueError("end must be after start")
        days = (end - start).days if end > start else 0  # Exclude end date, 0 for same day
        factor = days / 360
        return DayCountFactor(
            primary_period_fraction=factor,
            discount_factor_log=[f"{days}/360"]
        )
