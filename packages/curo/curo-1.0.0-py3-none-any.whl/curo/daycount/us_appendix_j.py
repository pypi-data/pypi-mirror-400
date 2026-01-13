"""
Implements the US Regulation Z, Appendix J day count convention for APR calculations.
"""

import pandas as pd
from curo.daycount.convention import Convention
from curo.daycount.day_count_factor import DayCountFactor
from curo.enums import DayCountTimePeriod
from curo.utils import actual_days, roll_month, roll_day, has_month_end_day, gauss_round

class USAppendixJ(Convention):
    # pylint: disable = C0301
    """
    The US Regulation Z, Appendix J day count convention for Annual Percentage Rate (APR).

    Used for closed-end credit transactions (e.g., mortgages) under the Truth in Lending Act.
    Defined in Appendix J, Paragraph (b)(3), treating months as equal and using specific
    denominators for odd days. Computes whole periods (e.g., months) and fractional adjustments
    for odd days using the discount formula:

    `d = a / ((1 + f * i / p) * (1 + i / p)^t)`

    Where:
        - `t`: Number of whole periods (e.g., months, years), stored as `primary_period_fraction`.
        - `f`: Fractional period for odd days (e.g., 5/30 for 5 days in a 30-day month), stored as
          `partial_period_fraction`.
        - `p`: Number of periods in a year (e.g., 12 for monthly, 365 for daily), included in
          `discount_terms_log`.

    See [Appendix J to Part 1026](https://www.ecfr.gov/current/title-12/chapter-X/part-1026/appendix-Appendix%20J%20to%20Part%201026)

    Denominators for odd days:
        - Year: 365
        - Half-year: 180
        - Quarter: 90
        - Month: 
        - Fortnight: 15
        - Week: 7
        - Daily periods: actual days / 365

    Aligns days or month-ends for whole period counts.

    Args:
        time_period (DayCountTimePeriod, optional): Interval for calculation (year, half-year,
            quarter, month, fortnight, week, day). Defaults to month.
    """
    def __init__(self, time_period: DayCountTimePeriod = DayCountTimePeriod.MONTH):
        self.time_period = time_period
        super().__init__(
            use_post_dates=True,
            include_non_financing_flows=True,
            use_xirr_method=True
        )

    def compute_factor(self, start: pd.Timestamp, end: pd.Timestamp) -> DayCountFactor:
        # pylint: disable = R0915:
        """
        Computes the day count factor between two dates using the US Appendix J convention.

        Args:
            start (pd.Timestamp): Initial drawdown date.
            end (pd.Timestamp): Cash flow post date.

        Returns:
            DayCountFactor: Factor with `primary_period_fraction` (t), `partial_period_fraction` (f),
                and `discount_terms_log` containing formatted operands (t, f, p).

        Raises:
            ValueError: If end is before start or unsupported time period.
        """
        if end < start:
            raise ValueError("end must be after start")
        if end == start:
            return DayCountFactor(
                primary_period_fraction=0.0,
                discount_terms_log=[
                    "t = 0",
                    "f = 0",
                    f"p = {self.time_period.periods_in_year}"]
            )

        whole_periods = 0
        initial_drawdown = start
        start_whole_period = end

        # Handle daily unit-periods
        if self.time_period == DayCountTimePeriod.DAY:
            days = actual_days(initial_drawdown, start_whole_period)
            days_in_year = DayCountTimePeriod.DAY.periods_in_year
            partial_period_fraction = days / days_in_year
            partial_period_operand = DayCountFactor.operands_to_string(days, days_in_year)
            return DayCountFactor(
                primary_period_fraction = 0.0, # No whole periods for daily
                partial_period_fraction = partial_period_fraction,
                discount_terms_log = [
                    "t = 0",
                    f"f = {partial_period_operand} = {gauss_round(partial_period_fraction, 8):.8f}",
                    f"p = {self.time_period.periods_in_year}"
                    ]
            )

        # Compute whole periods
        preferred_day = end.day
        if has_month_end_day(end):  # Apply EOM for any month-end end date
            preferred_day = 31  # Coerce roll_month to return last day of each month
        while start_whole_period > initial_drawdown:
            temp_date = start_whole_period
            if self.time_period == DayCountTimePeriod.YEAR:
                temp_date = roll_month(start_whole_period, -12, preferred_day)
            elif self.time_period == DayCountTimePeriod.HALF_YEAR:
                temp_date = roll_month(start_whole_period, -6, preferred_day)
            elif self.time_period == DayCountTimePeriod.QUARTER:
                temp_date = roll_month(start_whole_period, -3, preferred_day)
            elif self.time_period == DayCountTimePeriod.MONTH:
                temp_date = roll_month(start_whole_period, -1, preferred_day)
            elif self.time_period == DayCountTimePeriod.FORTNIGHT:
                temp_date = roll_day(start_whole_period, -14)
            elif self.time_period == DayCountTimePeriod.WEEK:
                temp_date = roll_day(start_whole_period, -7)
            else:
                raise ValueError(f"Unsupported time period: {self.time_period}") # pragma: no cover

            if self.time_period in [
                DayCountTimePeriod.YEAR,
                DayCountTimePeriod.HALF_YEAR,
                DayCountTimePeriod.QUARTER,
                DayCountTimePeriod.MONTH
            ]:
                if temp_date >= initial_drawdown:
                    start_whole_period = temp_date
                    whole_periods += 1
                else:
                    break
            else:  # FORTNIGHT, WEEK
                if temp_date >= initial_drawdown:
                    start_whole_period = temp_date
                    whole_periods += 1
                else:
                    break # pragma: no cover

        primary_period_fraction = float(whole_periods) if whole_periods > 0 else 0.0
        primary_period_operand = str(whole_periods) if whole_periods > 0 else ["0"]

        # Compute odd days
        partial_period_fraction = 0.0
        partial_period_operand = "0"
        if initial_drawdown <= start_whole_period:
            days = actual_days(initial_drawdown, start_whole_period)
            denominator = {
                DayCountTimePeriod.YEAR: 365,
                DayCountTimePeriod.HALF_YEAR: 180,
                DayCountTimePeriod.QUARTER: 90,
                DayCountTimePeriod.MONTH: 30,
                DayCountTimePeriod.FORTNIGHT: 15,
                DayCountTimePeriod.WEEK: 7
            }.get(self.time_period)
            if denominator is None:
                raise ValueError(f"Unsupported time period for denominator: {self.time_period}") # pragma: no cover
            if days > 0:
                partial_period_fraction = days / denominator
                partial_period_operand = f"{days}/{denominator} = {gauss_round(partial_period_fraction, 8):.8f}"

        return DayCountFactor(
            primary_period_fraction= primary_period_fraction,
            partial_period_fraction= partial_period_fraction,
            discount_terms_log = [
                f"t = {primary_period_operand}",
                f"f = {partial_period_operand}",
                f"p = {self.time_period.periods_in_year}" #used to convert annual rate to periodic rate
            ]
        )
