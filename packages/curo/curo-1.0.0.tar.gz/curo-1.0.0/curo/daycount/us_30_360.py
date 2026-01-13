"""
Implements the US 30/360 (Bond Basis) day count convention.
"""

import pandas as pd
from curo.daycount.convention import Convention
from curo.daycount.day_count_factor import DayCountFactor
from curo.enums import DayCountOrigin

class US30360(Convention):
    """
    The US 30/360 day count convention, also known as Bond Basis or 30/360.

    Computes the number of days in a period divided by 360, using the formula:

    `f = [(360 * (Y2 - Y1)) + (30 * (M2 - M1)) + (D2 - D1)] / 360`

    Where:
        - Y1, Y2: Years of the start and end dates.
        - M1, M2: Months of the start and end dates.
        - D1: Start day, set to 30 if 31.
        - D2: End day, set to 30 if 31 and D1 >= 30, otherwise as is.

    Used for bond and mortgage calculations in the US.

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

    def compute_factor(self, start: pd.Timestamp, end: pd.Timestamp) -> DayCountFactor:
        """
        Computes the day count factor between two dates using the US 30/360 convention.

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

        dd1 = start.day
        mm1 = start.month
        yyyy1 = start.year
        dd2 = end.day
        mm2 = end.month
        yyyy2 = end.year

        # Adjust D1: If day is 31, set to 30
        d1 = 30 if dd1 == 31 else dd1

        # Adjust D2: If day is 31 and D1 >= 30, set to 30; else use as is
        if dd2 == 31 and (d1 == 30 or dd1 == 31):
            d2 = 30
        elif dd2 == 31 and d1 < 30:
            d2 = dd2
        else:
            d2 = dd2

        # Compute numerator: [360 * (Y2 - Y1)] + [30 * (M2 - M1)] + (D2 - D1)
        numerator = (360 * (yyyy2 - yyyy1)) + (30 * (mm2 - mm1)) + (d2 - d1)
        factor = numerator / 360

        # Format operands
        return DayCountFactor(
            primary_period_fraction = factor,
            discount_factor_log = [DayCountFactor.operands_to_string(numerator, 360)]
        )
