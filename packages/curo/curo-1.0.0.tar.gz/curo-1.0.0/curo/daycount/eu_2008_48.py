"""
Implements the EU 2008/48/EC day count convention for APRC calculations.
"""

import pandas as pd
from curo.daycount.convention import Convention
from curo.daycount.day_count_factor import DayCountFactor
from curo.enums import DayCountTimePeriod
from curo.utils import roll_day, roll_month, has_month_end_day, actual_days

class EU200848EC(Convention):
    """
    The EU Directive 2008/48/EC day count convention for Annual Percentage Rate of Charge (APRC).

    Used for consumer credit agreements in EU member states. Computes time intervals backwards
    from the cash flow date to the initial drawdown date, expressed as whole periods (years,
    months, or weeks) plus remaining days divided by 365 or 366 (leap year).

    For more details, see [EU APR guidelines](../../assets/reference/eu_apr_guidelines_final.pdf)
    (ANNEX 1, section 4.1.1). This document is no longer available online and is provided
    here for reference.

    Note:
        Replaced by Directive (EU) 2023/2225, but this implementation remains valid as it
        expresses intervals as whole periods plus days, per Annex III, I. (c).

    Args:
        time_period (DayCountTimePeriod, optional): The interval for calculations ('year',
            'month', 'week'). Defaults to 'month'.
    """
    def __init__(self, time_period: DayCountTimePeriod = DayCountTimePeriod.MONTH):
        if time_period not in [
            DayCountTimePeriod.YEAR,
            DayCountTimePeriod.MONTH,
            DayCountTimePeriod.WEEK
        ]:
            raise ValueError("Only year, month, and week time periods are supported")
        self.time_period = time_period
        super().__init__(
            use_post_dates=True,
            include_non_financing_flows=True,
            use_xirr_method=True
        )

    def compute_factor(self, start: pd.Timestamp, end: pd.Timestamp) -> DayCountFactor:
        """
        Computes the day count factor between two dates using the EU 2008/48/EC convention.

        Calculates intervals backwards from the end date to the start date, expressed as whole
        periods (years, months, or weeks) plus remaining days divided by 365 or 366.

        Args:
            start (pd.Timestamp): Initial drawdown date.
            end (pd.Timestamp): Cash flow post date.

        Returns:
            DayCountFactor: The day count factor with year fraction and operands.

        Raises:
            ValueError: If end is before start.
        """
        if end < start:
            raise ValueError("end must be after start")
        if end == start:
            return DayCountFactor(primary_period_fraction=0.0, discount_factor_log=["0"])

        whole_periods = 0
        initial_drawdown = start
        start_whole_period = end
        operand_log = []

        while True:
            temp_date = None
            if self.time_period == DayCountTimePeriod.YEAR:
                temp_date = roll_month(start_whole_period, -12, end.day)
            elif self.time_period == DayCountTimePeriod.MONTH:
                temp_date = roll_month(start_whole_period, -1, end.day)
            elif self.time_period == DayCountTimePeriod.WEEK:
                temp_date = roll_day(start_whole_period, -7)

            if not initial_drawdown > temp_date:
                start_whole_period = temp_date
                whole_periods += 1
            else:
                # Handle month-end cases for year/month periods
                if self.time_period in [DayCountTimePeriod.YEAR, DayCountTimePeriod.MONTH]:
                    if self.time_period == DayCountTimePeriod.YEAR:
                        if (initial_drawdown.month == temp_date.month and
                            initial_drawdown.day == temp_date.day):
                            break
                        if (start.month == end.month and
                            has_month_end_day(start) and
                            has_month_end_day(end)):
                            start_whole_period = initial_drawdown
                            whole_periods += 1
                    elif self.time_period == DayCountTimePeriod.MONTH:
                        if initial_drawdown.day == temp_date.day:
                            break
                        if (initial_drawdown.day >= temp_date.day and
                            has_month_end_day(start) and
                            has_month_end_day(end)):
                            start_whole_period = initial_drawdown
                            whole_periods += 1
                break

        factor = 0.0
        if whole_periods > 0:
            factor = whole_periods / self.time_period.periods_in_year
            operand_log.append(
                DayCountFactor.operands_to_string(whole_periods, self.time_period.periods_in_year)
            )

        if not initial_drawdown > start_whole_period:
            numerator = actual_days(initial_drawdown, start_whole_period)
            start_den_period = roll_month(start_whole_period, -12, start_whole_period.day)
            denominator = actual_days(
                start_den_period,
                start_whole_period) if numerator > 0 else self.time_period.periods_in_year

            factor += numerator / denominator
            if numerator > 0 or not operand_log:
                operand_log.append(
                    DayCountFactor.operands_to_string(numerator, denominator)
                )

        return DayCountFactor(primary_period_fraction=factor, discount_factor_log=operand_log)
