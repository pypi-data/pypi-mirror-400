"""
Implements the Actual/Actual (ISDA) day count convention.
"""

import calendar
import pandas as pd
from curo.daycount.convention import Convention
from curo.daycount.day_count_factor import DayCountFactor

class ActualISDA(Convention):
    """
    Implements the Actual/Actual (ISDA) day count convention.

    Counts the actual number of days between two dates, including the end date for each
    year segment, and divides by 365 (non-leap year) or 366 (leap year). For multi-year
    periods, splits the calculation by year, summing fractions for each year. Suitable
    for compound interest calculations and XIRR when `use_xirr_method` is True.

    Args:
        use_post_dates: If True, uses cash flow post dates for day counts; if False, uses
            value dates. Defaults to True.
        include_non_financing_flows: If True, includes non-financing cash flows (e.g., fees)
            in factor computations; if False, excludes them. Defaults to False.
        use_xirr_method: If True, uses the XIRR method, setting day count origin to
            DRAWDOWN; if False, uses NEIGHBOUR. Defaults to False.

    Examples:
        >>> dc = ActualISDA()
        >>> factor = dc.compute_factor(
        ...     pd.Timestamp('2020-01-28', tz='UTC'),
        ...     pd.Timestamp('2020-02-28', tz='UTC')
        ... )
        >>> print(factor)
        f = 31/366 = 0.08469945
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
        Computes the year fraction between two dates using Actual/Actual (ISDA).

        Args:
            start: The earlier date (pd.Timestamp).
            end: The later date (pd.Timestamp).

        Returns:
            DayCountFactor: The year fraction with operand log.

        Raises:
            ValueError: If `end` is before `start`.

        Examples:
            >>> dc = ActualISDA()
            >>> factor = dc.compute_factor(
            ...     pd.Timestamp('2020-01-28', tz='UTC'),
            ...     pd.Timestamp('2020-02-28', tz='UTC')
            ... )
            >>> factor.primary_period_fraction
            0.08469945355191257
            >>> factor.discount_factor_log
            ['31/366']
        """
        if end < start:
            raise ValueError("end must be after start")
        if end == start:
            return DayCountFactor(primary_period_fraction=0.0, discount_factor_log=["0/365"])

        start_year = start.year
        end_year = end.year
        factor = 0.0

        if start_year == end_year:
            # Same year: use single denominator (365 or 366)
            days = (end - start).days
            denominator = 366 if calendar.isleap(start_year) else 365
            factor = days / denominator
            return DayCountFactor(
                primary_period_fraction=factor,
                discount_factor_log=[f"{days}/{denominator}"]
            )

        # Multi-year: split by year
        discount_factor_log = []
        current_date = start
        current_year = start_year

        while current_year != end_year:
            year_end = pd.Timestamp(f"{current_year}-12-31", tz="UTC")
            days = (year_end - current_date).days + 1 if year_end >= current_date else 0
            denominator = 366 if calendar.isleap(current_year) else 365
            factor += days / denominator
            discount_factor_log.append(f"{days}/{denominator}")
            current_date = year_end + pd.Timedelta(days=1)  # Move to Jan 1 next year
            current_year += 1

        # Final partial year
        days = (end - current_date).days if end >= current_date else 0
        denominator = 366 if calendar.isleap(end_year) else 365
        if days > 0:
            factor += days / denominator
            discount_factor_log.append(f"{days}/{denominator}")

        return DayCountFactor(
            primary_period_fraction=factor,
            discount_factor_log=discount_factor_log
        )
