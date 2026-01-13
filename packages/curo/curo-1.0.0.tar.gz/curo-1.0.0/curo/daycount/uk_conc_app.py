"""
Implements the UK CONC App day count convention for APRC calculations.
"""

import calendar
import pandas as pd
from curo.daycount.convention import Convention
from curo.daycount.day_count_factor import DayCountFactor
from curo.enums import DayCountTimePeriod
from curo.utils import actual_days, roll_month, roll_day, has_month_end_day

class UKConcApp(Convention):
    """
    The UK CONC App day count convention for Annual Percentage Rate of Charge (APRC).

    Used for consumer credit agreements under the Financial Services and Markets Act 2000.

    Supports two contexts:
        - Secured on land (CONC App 1.1): Mortgage-related agreements.
        - Not secured on land (CONC App 1.2): Other consumer credit agreements.

    See FCA Handbook [CONC App 1.1](https://www.handbook.fca.org.uk/handbook/CONC/App/1/1.html)
    and [CONC App 1.2](https://www.handbook.fca.org.uk/handbook/CONC/App/1/2.html)

    Computes intervals from the first drawdown date in years or fractions:
        - Year = 365 days (366 in leap years), 52 weeks, or 12 equal months.
        - Whole months (1/12 year) or weeks (1/52 year) if exact.
        - For secured agreements with single payments, uses months for whole-month periods.
        - Non-whole periods: Whole months or weeks, then residual days (1/365 or 1/366).

    Args:
        is_secured_on_land (bool, optional): True for agreements secured on land (CONC App 1.1).
            Defaults to False.
        has_single_payment (bool, optional): True for single-payment profiles, forces months
            for whole-month periods if is_secured_on_land=True. Defaults to False.
        time_period (DayCountTimePeriod, optional): Repayment frequency ('month' or 'week').
            Defaults to 'month'.
    """
    def __init__(
        self,
        is_secured_on_land: bool = False,
        has_single_payment: bool = False,
        time_period: DayCountTimePeriod = DayCountTimePeriod.MONTH
    ):
        if time_period not in [DayCountTimePeriod.MONTH, DayCountTimePeriod.WEEK]:
            raise ValueError("Only month and week time periods are supported")
        self.is_secured_on_land = is_secured_on_land
        self.has_single_payment = has_single_payment
        self.time_period = time_period
        super().__init__(
            use_post_dates=True,
            include_non_financing_flows=True,
            use_xirr_method=True
        )

    def _has_conc_month_end_day(self, date: pd.Timestamp) -> bool:
        """
        Checks if a date is the last day of its month per UK CONC App rules.

        Treats both Feb 28 and Feb 29 as month-end in leap years for consistency
        with calendar month spans (e.g., Jan 31 to Feb 28 = 1 month).

        Args:
            date (pd.Timestamp): The date to check.

        Returns:
            bool: True if the date is the last day of the month per CONC rules, False otherwise.
        """
        if date.month == 2 and calendar.isleap(date.year):
            return date.day in [28, 29]
        return has_month_end_day(date)

    def _months_between_dates(self, date1: pd.Timestamp, date2: pd.Timestamp) -> int:
        """
        Computes the number of months between two dates, adjusting for day differences.

        Args:
            date1 (pd.Timestamp): Start date.
            date2 (pd.Timestamp): End date.

        Returns:
            int: Number of months, with adjustment if days differ and not both month-end.
        """
        if date1 > date2:
            date1, date2 = date2, date1
        month_adj = -1 if date1.day > date2.day and not (
            self._has_conc_month_end_day(date1) and self._has_conc_month_end_day(date2)
        ) else 0
        return (date2.year - date1.year) * 12 + (date2.month - date1.month) + month_adj

    def compute_factor(self, start: pd.Timestamp, end: pd.Timestamp) -> DayCountFactor:
        """
        Computes the day count factor between two dates using the UK CONC App convention.

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
            return DayCountFactor(
                primary_period_fraction=0.0, discount_factor_log=["0"])

        whole_periods = 0
        factor = 0.0
        operand_log = []

        is_same_dated = (end - start).days == 0
        is_whole_number_of_weeks = not is_same_dated and actual_days(start, end) % 7 == 0
        is_whole_number_of_months = not is_same_dated and (
            start.day == end.day or (
                self._has_conc_month_end_day(start) and self._has_conc_month_end_day(end)
            )
        )

        if self.time_period == DayCountTimePeriod.WEEK:
            whole_periods = actual_days(start, end) // 7
            if is_whole_number_of_weeks:
                if (self.is_secured_on_land and
                    is_whole_number_of_months and
                    self.has_single_payment):
                    whole_periods = self._months_between_dates(start, end)
                    factor = whole_periods / DayCountTimePeriod.MONTH.periods_in_year
                    operand_log.append(
                        DayCountFactor.operands_to_string(
                            whole_periods, DayCountTimePeriod.MONTH.periods_in_year
                        )
                    )
                    return DayCountFactor(
                        primary_period_fraction=factor, discount_factor_log=operand_log)
                factor = whole_periods / self.time_period.periods_in_year
                operand_log.append(
                    DayCountFactor.operands_to_string(
                        whole_periods,
                        self.time_period.periods_in_year)
                )
                return DayCountFactor(
                    primary_period_fraction=factor, discount_factor_log=operand_log)
        else:  # MONTH
            whole_periods = self._months_between_dates(start, end)
            if is_whole_number_of_months:
                factor = whole_periods / self.time_period.periods_in_year
                operand_log.append(
                    DayCountFactor.operands_to_string(
                        whole_periods,
                        self.time_period.periods_in_year)
                )
                return DayCountFactor(
                    primary_period_fraction=factor, discount_factor_log=operand_log)

        # Non-whole periods: whole units then residual days
        factor = whole_periods / self.time_period.periods_in_year
        if whole_periods > 0:
            operand_log.append(
                DayCountFactor.operands_to_string(whole_periods, self.time_period.periods_in_year)
            )
        whole_period_end = (
            roll_day(start, whole_periods * 7) if self.time_period == DayCountTimePeriod.WEEK
            else roll_month(start, whole_periods, start.day)
        )

        factor = self._process_remaining_days(end, whole_period_end, factor, operand_log)
        return DayCountFactor(primary_period_fraction=factor, discount_factor_log=operand_log)

    def _process_remaining_days(
        self,
        end: pd.Timestamp,
        whole_period_end: pd.Timestamp,
        factor: float,
        operand_log: list
    ) -> float:
        """
        Processes residual days after whole periods, adjusting for year boundaries.

        Args:
            end (pd.Timestamp): End date.
            whole_period_end (pd.Timestamp): Date after whole periods.
            factor (float): Current factor value.
            operand_log (list): List of operand strings.

        Returns:
            float: Updated factor with residual days.
        """
        if whole_period_end.year == end.year:
            days_remaining = (end - whole_period_end).days
            days_in_year = 366 if calendar.isleap(end.year) else 365
            factor += days_remaining / days_in_year
            operand_log.append(DayCountFactor.operands_to_string(days_remaining, days_in_year))
        else:
            year_end = pd.Timestamp(whole_period_end.year, 12, 31, tz='UTC')
            days_remaining = (year_end - whole_period_end).days
            days_in_year = 366 if calendar.isleap(whole_period_end.year) else 365
            factor += days_remaining / days_in_year
            operand_log.append(DayCountFactor.operands_to_string(days_remaining, days_in_year))

            days_remaining = (end - year_end).days
            days_in_year = 366 if calendar.isleap(end.year) else 365
            factor += days_remaining / days_in_year
            operand_log.append(DayCountFactor.operands_to_string(days_remaining, days_in_year))

        return factor
