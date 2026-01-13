"""
Implements the 30/360 (EU) day count convention.
"""

import pandas as pd
from curo.daycount.convention import Convention
from curo.daycount.day_count_factor import DayCountFactor

class EU30360(Convention):
    """
    The 30/360 (EU) day count convention, also known as '30E/360' or 'Eurobond basis'.

    Computes the number of days in a period divided by 360, using the formula:
        
    `f = [[360 * (Y2 - Y1)] + [30 * (M2 - M1)] + (D2 - D1)] / 360`

    Where:
        - Y1, Y2: Years of the start and end dates.
        - M1, M2: Months of the start and end dates.
        - D1: First calendar day, adjusted to 30 if 31.
        - D2: End calendar day, adjusted to 30 if 31.

    Args:
        use_post_dates (bool, optional): Whether to use post dates for cash flow day counts.
            Defaults to True.
        include_non_financing_flows (bool, optional): Whether to include non-financing cash flows
            in periodic factor computations. Defaults to False.
        use_xirr_method (bool, optional): Whether to use XIRR method for time periods,
            referencing the first cash flow date. Defaults to False.
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
        Computes the day count factor between two dates using the EU 30/360 convention.

        Args:
            start (pd.Timestamp): Start date of the period.
            end (pd.Timestamp): End date of the period.

        Returns:
            DayCountFactor: The day count factor with year fraction and operands.
        
        Raises:
            ValueError: If `end` is before `start`.
        """
        if end < start:
            raise ValueError("end must be after start")
        if end == start:
            return DayCountFactor(primary_period_fraction=0.0, discount_factor_log=["0/360"])

        dd1 = start.day
        mm1 = start.month
        yyyy1 = start.year
        dd2 = end.day
        mm2 = end.month
        yyyy2 = end.year

        # Adjust day to 30 if 31
        z = 30 if dd1 == 31 else dd1
        dt1 = 360 * yyyy1 + 30 * mm1 + z

        z = 30 if dd2 == 31 else dd2
        dt2 = 360 * yyyy2 + 30 * mm2 + z

        numerator = abs(dt2 - dt1)
        factor = numerator / 360
        return DayCountFactor(
            primary_period_fraction=factor,
            discount_factor_log=[DayCountFactor.operands_to_string(numerator, 360)]
        )
 