"""
Defines the abstract base class for day count conventions in financial calculations.
"""

import pandas as pd
from curo.daycount.day_count_factor import DayCountFactor
from curo.enums import DayCountOrigin

class Convention:
    """
    Abstract base class for day count conventions in financial calculations.

    Day count conventions calculate the fraction of a year between two dates for interest
    calculations, such as APR or IRR. Subclasses must implement the `compute_factor` method.

    Args:
        use_post_dates: If True, uses cash flow post dates for day counts; if False, uses value
            dates. Defaults to False, as value dates are typically used for IRR calculations
            with deferred settlements (e.g., 0% interest promotions).
        include_non_financing_flows: If True, includes non-financing cash flows (e.g., fees)
            in periodic factor computations; if False, excludes them. Defaults to False, but
            True may be required for APRC calculations under EU consumer credit and similar laws.
        use_xirr_method: If True, uses the XIRR method, setting the day count origin to
            DRAWDOWN; if False, uses NEIGHBOUR. Defaults to False.

    See Also:
        DayCountFactor: The return type for `compute_factor`.
        DayCountOrigin: Defines the origin for day count calculations.
    """
    def __init__(self,
                 use_post_dates: bool = False,
                 include_non_financing_flows: bool = False,
                 use_xirr_method: bool = False
                 ):
        self.use_post_dates = use_post_dates
        self.include_non_financing_flows = include_non_financing_flows
        self.use_xirr_method = use_xirr_method

    def compute_factor(self, start: pd.Timestamp, end: pd.Timestamp) -> DayCountFactor:
        """
        Computes the year fraction between two dates for the day count convention.

        Args:
            start: The earlier date (pd.Timestamp).
            end: The later date (pd.Timestamp).

        Returns:
            DayCountFactor: The year fraction for the period.

        Raises:
            NotImplementedError: If not implemented by a subclass.
        """
        raise NotImplementedError

    @property
    def day_count_origin(self) -> DayCountOrigin:
        """
        The start date origin for day count calculations, based on `use_xirr_method`.

        Returns:
            DayCountOrigin: DRAWDOWN if `use_xirr_method` is True, else NEIGHBOUR.
        """
        return DayCountOrigin.DRAWDOWN if self.use_xirr_method else DayCountOrigin.NEIGHBOUR
