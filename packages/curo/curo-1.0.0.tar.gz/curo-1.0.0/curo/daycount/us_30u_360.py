"""
Implements the US 30U/360 day count convention, a variant of US 30/360.
"""

import calendar
import pandas as pd
from curo.daycount.convention import Convention
from curo.daycount.day_count_factor import DayCountFactor
from curo.enums import DayCountOrigin
from curo.utils import has_month_end_day

class US30U360(Convention):
    """
    The US 30U/360 day count convention, a variant of US 30/360 (Bond Basis).

    Computes the number of days in a period divided by 360, using the formula:

    `f = [(360 * (Y2 - Y1)) + (30 * (M2 - M1)) + (D2 - D1)] / 360`

    Note: Differs from US 30/360 in February handling
        - February has 30 days if start or end date is Feb 28 (non-leap year) or
            Feb 29 (leap year).
        - Exception: In non-leap years, if start or end date is Feb 29, February 
            has 29 days.
        - D1 = 30 if start day is 31.
        - D2 = 30 if end day is 31.

    Used for specific financial calculations, aligning with tools like the HP12C calculator.

    Args:
        use_post_dates (bool, optional): If True, uses cash flow post dates. Defaults to True.
        include_non_financing_flows (bool, optional): If True, includes non-financing flows.
            Defaults to False.
        use_xirr_method (bool, optional): If True, uses XIRR method with drawdown origin.
            Defaults to False.
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

    @property
    def day_count_origin(self) -> DayCountOrigin:
        """
        Returns the day count origin based on the XIRR method.

        Returns:
            DayCountOrigin: NEIGHBOUR if use_xirr_method is False, DRAWDOWN otherwise.
        """
        return DayCountOrigin.DRAWDOWN if self.use_xirr_method else DayCountOrigin.NEIGHBOUR

    def _day_difference(self, start: pd.Timestamp, end: pd.Timestamp, d1: int, d2: int) -> int:
        """
        Computes the day difference (D2 - D1) with US 30U/360 February adjustments.

        Args:
            start (pd.Timestamp): Start date for month-end checks.
            end (pd.Timestamp): End date for month-end checks.
            d1 (int): Adjusted start day (30 if 31).
            d2 (int): Adjusted end day (30 if 31).

        Returns:
            int: Adjusted day difference.
        """
        is_d1_last_day = has_month_end_day(start)
        is_d2_last_day = has_month_end_day(end)

        if is_d1_last_day and is_d2_last_day:
            return d2 + (d1 - d2) - d1  # Simplifies to 0 for same-day month-ends
        if is_d1_last_day and start.month == 2 and d1 != d2:
            if not calendar.isleap(start.year) and d2 == 29:
                return d2 - (d1 + (29 - d1))
            return d2 - (d1 + (30 - d1))
        if is_d2_last_day and end.month == 2 and d2 != d1:
            if not calendar.isleap(end.year) and d1 == 29:
                return (d2 + (29 - d2)) - d1
            return (d2 + (30 - d2)) - d1
        return d2 - d1

    def compute_factor(self, start: pd.Timestamp, end: pd.Timestamp) -> DayCountFactor:
        """
        Computes the day count factor between two dates using the US 30U/360 convention.

        Args:
            start (pd.Timestamp): Start date of the period.
            end (pd.Timestamp): End date of the period.

        Returns:
            DayCountFactor: The day count factor with year fraction and operands.

        Raises:
            ValueError: If end is before start.
        """
        if end < start:
            raise ValueError("end must be after start")
        if end == start:
            return DayCountFactor(primary_period_fraction=0.0, discount_factor_log=["0"])

        # Adjust days: Set to 30 if 31
        d1 = 30 if start.day == 31 else start.day
        d2 = 30 if end.day == 31 else end.day

        # Compute day difference with February adjustments
        days_diff = self._day_difference(start, end, d1, d2)

        # Compute numerator: [360 * (Y2 - Y1)] + [30 * (M2 - M1)] + (D2 - D1)
        numerator = ((end.year - start.year) * 360) + ((end.month - start.month) * 30) + days_diff
        factor = numerator / 360

        # Format operands
        operand = str(int(factor)) if numerator % 360 == 0 else f"{numerator}/360"
        operand_log = [operand]

        return DayCountFactor(primary_period_fraction=factor, discount_factor_log=operand_log)
