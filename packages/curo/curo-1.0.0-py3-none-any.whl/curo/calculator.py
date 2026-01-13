# pylint: disable=C0301:line-too-long
"""
calculator.py

This module provides the Calculator class for performing financial calculations on cash flow series,
including solving for effective interest rates and unknown cash flow amounts. It supports various
day count conventions (e.g., US30360, USAppendixJ) and aligns with the Dart library for accuracy 
in loan amortization and APR calculations.

Key Features:
- Solves for interest rates (`solve_rate`) to achieve a net future value (NFV) of zero.
- Solves for one or more unknown payment or advance amounts (`solve_value`) 
    with weighted adjustments.
- Supports bespoke cash flow profiles (DataFrame) or series-based profiles (Series objects).
- Handles USAppendixJ periodic rate conversions and interest amortization.
- Provides precise, unrounded calculations with optional rounding to specified precision.
- Validates cash flow profiles for consistency and solvability.

Usage:
    from curo import Calculator, SeriesAdvance, SeriesPayment, US30360
    calc = Calculator(precision=2)
    calc.add(...)  # Add advance and payment cash flow series
    rate = calc.solve_rate(US30360(), upper_bound=10.0)
    value = calc.solve_value(US30360(), interest_rate=0.12)

The module integrates with pandas for DataFrame operations and scipy for numerical root-finding,
ensuring robust and efficient calculations.
"""

from typing import Optional
import pandas as pd
import scipy.optimize
from curo.daycount.convention import Convention
from curo.daycount.us_appendix_j import USAppendixJ
from curo.enums import (
    CashFlowColumn as Column,
    CashFlowColumnExtras as ColumnExtras,
    DayCountOrigin,
    Mode,
    SortColumn,
    ValidationMode)
from curo.exceptions import UnsolvableError, ValidationError
from curo.series import (
    Series,
    SeriesAdvance,
    SeriesPayment,
    SeriesCharge)
from curo.utils import roll_date, gauss_round, to_timestamp

class Calculator:
    """
    The Calculator class provides the entry point for solving unknown values and/or
    unknown interest rates implicit in a cash flow series.

    Args:
        precision (int): Number of fractional digits for rounding cash flow values in
            the notional currency. Must be between 0 and 4 (inclusive). Defaults to 2.
        profile (pd.DataFrame, optional): A bespoke pandas DataFrame containing dated
            cash flow data. Use with caution, as bespoke profiles bypass internal series
            validation and may lead to inconsistent data. Defaults to None.

    Attributes:
        precision (int): The rounding precision for cash flow values.
        profile (pd.DataFrame or None): The DataFrame containing cash flow data.
        _series (List[Series]): Private list of provided cash flow series.
        _is_bespoke_profile (bool): Used internally to identify profile source.

    Raises:
        ValidationError: If precision is not between 0 and 4.

    Returns:
        Calculator: A new Calculator instance configured with the specified precision
            and optional profile.
    """
    def __init__(self, precision: int = 2, profile: Optional[pd.DataFrame] = None) -> "Calculator":
        if not 0 <= precision <= 4:
            raise ValidationError("Precision must be between 0 and 4")
        self.precision = precision
        self.profile = profile
        self._series = []
        self._is_bespoke_profile = profile is not None

    def add(self, series: Series) -> None:
        """
        Adds a cash flow series to the series list.

        Args:
            series (Series): An instance of Series (e.g., SeriesAdvance, SeriesPayment,
                or SeriesCharge) representing one or more advances, payments, or charges.

        Returns:
            None

        Raises:
            ValidationError: If a bespoke profile is set, as series cannot be added in this mode.

        Notes:
            - The order of addition matters for `undated` series, as their cash flow dates
                are inferred from the order in the series list, with later additions following
                previous ones.
            - `Dated` series use their provided start date and are unaffected by order.
            - If `series.amount` is not None, it is rounded to the Calculator's precision.
        """
        if self._is_bespoke_profile:
            raise ValidationError("Cannot add series with a bespoke profile")
        if series.amount is not None:
            # Coerce series monetary value to specified precision
            series.amount = gauss_round(series.amount, self.precision)
        self._series.append(series)

    def solve_value(
        self,
        convention: Convention,
        interest_rate: float,
        start_date: Optional[pd.Timestamp] = None) -> float:
        """
        Solves for one or more unknown payment or advance cash flow amounts to achieve
        a net future value (NFV) of zero.

        Args:
            convention (Convention): Day count convention (e.g., US30360, USAppendixJ).
            interest_rate (float): Annualized interest rate (e.g., 0.12 for 12%).
            start_date (pd.Timestamp, optional): The start date for constructing the
                cash flow profile for `undated` series. Defaults to the current system 
                date if None.

        Returns:
            float: The raw cash flow amount (before weightings), unrounded.

        Raises:
            ValidationError: If inputs are invalid (e.g., no cash flows, no unknowns).
            UnsolvableError: If no amount can be found to achieve NFV = 0.

        Notes:
            - Uses scipy.optimize.brentq to find the base amount where NFV = 0.
            - Supports bespoke profiles (self.profile) or series-based profiles (self._series).
            - For USAppendixJ, converts the interest rate to periodic.
            - The returned value is the raw amount before applying weightings. For weighted
                payments, multiply by each series' `weighting` to get the final amount for
                 or APR schedules.
            - Updates self.profile with solved amounts and, if not use_xirr_method,
                amortizes interest.
        """
        # Build, sort, and validate cash flow profile
        if self._is_bespoke_profile:
            if not isinstance(self.profile, pd.DataFrame) or self.profile.empty:
                raise ValidationError("Bespoke profile must be a non-empty DataFrame")
            cash_flows = self.profile
        else:
            if not self._series:
                raise ValidationError("No cash flow series provided")
            cash_flows = self._build_profile(start_date)

        sort_by = SortColumn.POST_DATE if convention.use_post_dates else SortColumn.VALUE_DATE
        cash_flows = self._sort_cash_flows(cash_flows, sort_by=sort_by)
        self._validate_profile(
            df=cash_flows,
            sort_by=sort_by,
            mode=ValidationMode.SOLVE_VALUE
        )

        # Assign day count factors
        cash_flows = self._assign_factors(cash_flows, convention)

        if isinstance(convention, USAppendixJ):
            # USAppendixJ uses periodic rate
            interest_rate /= convention.time_period.periods_in_year

        # Define NFV function for root-finding
        def nfv_function(value: float) -> float:
            cash_flows_copy = cash_flows.copy()
            cash_flows_copy = self._update_unknowns(
                cash_flows_copy, value, precision=self.precision, is_rounded=True
            )
            return self._calculate_nfv(cash_flows_copy, convention, interest_rate)

        # Solve for base value where NFV = 0
        try:
            value = scipy.optimize.brentq(
                nfv_function,
                a=-1e6,  # Generous bounds
                b=1e6,
                xtol=1e-8,
                rtol=1e-8,
                maxiter=100
            )
        except ValueError as e:
            raise UnsolvableError("No amount found to achieve NFV = 0") from e

        # Update profile with solved values
        self.profile = self._update_unknowns(
            cash_flows, value, precision=self.precision, is_rounded=True
        )

        return gauss_round(value, self.precision)

    def solve_rate(
        self,
        convention: Convention,
        start_date: Optional[pd.Timestamp] = None,
        upper_bound: float = 10.0) -> float:
        """
        Computes the effective interest rate that results in a net future value (NFV) of zero.

        Args:
            convention (Convention): Day count convention (e.g., US30360, USAppendixJ).
            start_date (pd.Timestamp, optional): The start date for constructing the
                cash flow profile for `undated` series. Defaults to the current system 
                date if None.
            upper_bound (float): Upper bound for the interest rate search (default: 10.0, or 1000%).

        Returns:
            float: The effective interest rate (annualized), unrounded.

        Raises:
            ValidationError: If inputs are invalid (e.g., no series, invalid upper_bound).
            UnsolvableError: If no rate can be found within bounds.

        Notes:
            - If called after solve_value, uses the existing profile (if it has a 'factor' column)
              and sets all is_known to True to ensure validation passes for SOLVE_RATE mode.
            - Always assigns day count factors based on the provided convention, as it may differ
              from the convention used in solve_value.
            - Uses scipy.optimize.brentq for root-finding within [-0.9999, upper_bound].
            - For USAppendixJ, the periodic rate is annualized by multiplying by periods_in_year.
        """
        if upper_bound <= 0.0:
            raise ValidationError("Upper bound must be positive")

        # Build, sort, and validate cash flow profile
        if self._is_bespoke_profile:
            if not isinstance(self.profile, pd.DataFrame) or self.profile.empty:
                raise ValidationError("Bespoke profile must be a non-empty DataFrame")
            cash_flows = self.profile.copy()
        else:
            # Check if profile exists and has a 'factor' column (indicating solve_value was called)
            if (self.profile is not None and
                    isinstance(self.profile, pd.DataFrame) and
                    not self.profile.empty and
                    ColumnExtras.FACTOR.value in self.profile.columns):
                cash_flows = self.profile.copy()  # Use existing profile
                # Set all is_known to True to pass SOLVE_RATE validation
                cash_flows[Column.IS_KNOWN.value] = True
            else:
                if not self._series:
                    raise ValidationError("No cash flow series provided")
                cash_flows = self._build_profile(start_date)

        sort_by = SortColumn.POST_DATE if convention.use_post_dates else SortColumn.VALUE_DATE
        cash_flows = self._sort_cash_flows(cash_flows, sort_by=sort_by)
        self._validate_profile(
            df=cash_flows,
            sort_by=sort_by,
            mode=ValidationMode.SOLVE_RATE
            )

        # Assign day count factors based on the provided convention
        cash_flows = self._assign_factors(cash_flows, convention)

        # Define NFV function for root-finding
        def nfv_function(rate: float) -> float:
            return self._calculate_nfv(cash_flows, convention, rate)

        # Solve for rate where NFV = 0
        try:
            rate = scipy.optimize.brentq(
                nfv_function,
                a=-0.9999,
                b=upper_bound,
                xtol=1e-8,
                rtol=1e-8,
                maxiter=100
            )
            # Update profile with cash flow values
            self.profile = cash_flows

            if isinstance(convention, USAppendixJ):
                # USAppendixJ solves for periodic rate, convert to annualized
                return rate * convention.time_period.periods_in_year
            return rate
        except ValueError as e:
            raise UnsolvableError(
                f"No interest rate found within bounds [-0.9999, {upper_bound}]") from e

    def build_schedule(
        self,
        profile: pd.DataFrame,
        convention: Convention,
        interest_rate: float
    ) -> pd.DataFrame:
        """
        Transforms the cash flow profile into an Amortization or APR proof schedule.

        Args:
            profile (pd.DataFrame): DataFrame containing cash flow data with CashFlowColumn columns.
            convention (Convention): Day count convention (e.g., US30360, USAppendixJ).
            interest_rate (float): Annual effective interest rate (e.g., 0.12 for 12%).

        Returns:
            pd.DataFrame: A DataFrame containing either an Amortization schedule (columns:
                post_date|value_date, label, amount, capital, interest, capital_balance) or
                an APR proof schedule (columns: post_date|value_date, label, amount,
                discount_log, amount_discounted, discounted_balance), depending on
                convention.use_xirr_method. For the APR proof schedule, discounted_balance
                shows the running total of amount_discounted, netting to zero.

        Raises:
            ValidationError: If inputs are invalid (e.g., negative interest rate, invalid profile,
                or undefined cash flow amounts).
        """
        if interest_rate < 0.0:
            raise ValidationError("Negative interest rate not permitted")

        schedule = profile.copy()

        # Check that the 'factor' column is present
        if ColumnExtras.FACTOR.value not in schedule.columns:
            raise ValidationError(
                "Cash flow profile must include a 'factor' column (run _assign_factors)")

        # Check that all AMOUNT values are defined (no NaN values)
        if schedule[Column.AMOUNT.value].isna().any():
            raise ValidationError("All cash flow amounts must be defined (no NaN values)")

        # Set IS_KNOWN=True for all rows to pass SOLVE_RATE validation
        schedule[Column.IS_KNOWN.value] = True

        sort_by = SortColumn.POST_DATE if convention.use_post_dates else SortColumn.VALUE_DATE
        schedule = self._sort_cash_flows(schedule, sort_by)
        self._validate_profile(schedule, sort_by, ValidationMode.SOLVE_RATE)

        # Determine the date column to include
        date_column = sort_by.value

        if convention.use_xirr_method:
            # APR Proof Schedule
            # Initialize output columns
            schedule[ColumnExtras.DISCOUNT_LOG.value] = ''
            schedule[ColumnExtras.AMOUNT_DISCOUNTED.value] = 0.0
            schedule[ColumnExtras.DISCOUNTED_BALANCE.value] = 0.0

            for idx, row in schedule.iterrows():
                factor = row[ColumnExtras.FACTOR.value]
                amount = row[Column.AMOUNT.value]
                discount_log = factor.to_folded_string()

                if isinstance(convention, USAppendixJ):
                    # Formula: d = a / ((1 + f * i / p) * (1 + i / p)^t)
                    f = factor.partial_period_fraction or 0.0
                    t = factor.primary_period_fraction
                    p = convention.time_period.periods_in_year
                    i = interest_rate
                    denominator = (1 + f * i / p) * (1 + i / p) ** t
                    amount_discounted = amount / denominator if denominator != 0 else amount
                else:
                    # Formula: d = a × (1 + i)^(-t)
                    t = factor.primary_period_fraction
                    i = interest_rate
                    amount_discounted = amount * (1 + i) ** (-t)

                schedule.at[
                    idx, ColumnExtras.DISCOUNT_LOG.value
                    ] = discount_log
                schedule.at[
                    idx, ColumnExtras.AMOUNT_DISCOUNTED.value
                    ] = gauss_round(amount_discounted, 6)

            # Compute running total for discounted_balance
            schedule[
                ColumnExtras.DISCOUNTED_BALANCE.value
                ] = schedule[ColumnExtras.AMOUNT_DISCOUNTED.value].cumsum().apply(
                lambda x: gauss_round(x, 6)
            )

            # Select required columns
            output_columns = [
                date_column,
                Column.LABEL.value,
                Column.AMOUNT.value,
                ColumnExtras.DISCOUNT_LOG.value,
                ColumnExtras.AMOUNT_DISCOUNTED.value,
                ColumnExtras.DISCOUNTED_BALANCE.value
        ]
            schedule = schedule[output_columns]

        else:
            # Amortization Schedule
            # Compute interest using existing _amortise_interest method
            schedule = self._amortise_interest(schedule, interest_rate, self.precision)
            # Initialize output columns
            schedule[ColumnExtras.CAPITAL.value] = 0.0
            schedule[ColumnExtras.CAPITAL_BALANCE.value] = 0.0

            capital_balance = 0.0
            for idx, row in schedule.iterrows():
                if row[Column.IS_CHARGE.value]:
                    continue  # Skip charges
                amount = row[Column.AMOUNT.value]
                interest = row[ColumnExtras.INTEREST.value]
                capital = amount + interest
                capital_balance += interest + amount

                schedule.at[
                    idx, ColumnExtras.CAPITAL.value
                    ] = gauss_round(capital, self.precision)
                schedule.at[
                    idx, ColumnExtras.CAPITAL_BALANCE.value
                    ] = gauss_round(capital_balance, self.precision)

            # Select required columns
            output_columns = [
                date_column,
                Column.LABEL.value,
                Column.AMOUNT.value,
                ColumnExtras.CAPITAL.value,
                ColumnExtras.INTEREST.value,
                ColumnExtras.CAPITAL_BALANCE.value
            ]
            schedule = schedule[output_columns]

        return schedule

    def _build_profile(self, start_date: Optional[pd.Timestamp] = None) -> pd.DataFrame:
        """
        Builds a cash flow DataFrame from the series list.

        Args:
            start_date (pd.Timestamp, optional): The start date for `undated` series.
                Defaults to the current system date if None.

        Returns:
            pd.DataFrame: A DataFrame containing cash flow data with columns defined by
                CashFlowColumn, with consistent dtypes.

        Notes:
            - For `undated` series, start dates are inferred from the order of series addition,
                with later series following the end date of previous ones.
            - `Dated` series use their provided `post_date_from`.
            - Advances have negative amounts, payments and charges have positive amounts.
            - An empty DataFrame with correct columns is returned if no series are present.
        """
        start_date = to_timestamp(start_date)
        if start_date is None:
            start_date = pd.Timestamp.now(tz='UTC').normalize()

        cash_flows_list = []
        advance_start_date = start_date
        payment_start_date = start_date
        charge_start_date = start_date
        for s in self._series:
            if isinstance(s, SeriesAdvance):
                if s.post_date_from is None and s.mode == Mode.ARREAR:
                    advance_start_date = roll_date(
                        advance_start_date,
                        s.frequency,
                        advance_start_date.day
                    )
                cf = s.to_cash_flows(advance_start_date
                                     if s.post_date_from is None
                                     else s.post_date_from)
                cf[Column.AMOUNT.value] = -abs(cf[Column.AMOUNT.value]) # Negate advance values
                cf[Column.IS_CHARGE.value] = False
                if s.post_date_from is None:
                    # Updated only for system defined dates
                    advance_start_date = cf[Column.POST_DATE.value].iloc[-1]
                    if s.mode == Mode.ADVANCE:
                        # Shift date to end of last period
                        advance_start_date = roll_date(
                            advance_start_date,
                            s.frequency,
                            advance_start_date.day
                        )
                cash_flows_list.append(cf)
            elif isinstance(s, SeriesPayment):
                if s.post_date_from is None and s.mode == Mode.ARREAR:
                    payment_start_date = roll_date(
                        payment_start_date,
                        s.frequency,
                        payment_start_date.day
                    )
                cf = s.to_cash_flows(payment_start_date
                                     if s.post_date_from is None
                                     else s.post_date_from)
                cf[Column.IS_INTEREST_CAPITALISED.value] = s.is_interest_capitalised
                cf[Column.IS_CHARGE.value] = False
                if s.post_date_from is None:
                    # Updated only for system defined dates
                    payment_start_date = cf[Column.POST_DATE.value].iloc[-1]
                    if s.mode == Mode.ADVANCE:
                        # Shift date to end of last period
                        payment_start_date = roll_date(
                            payment_start_date,
                            s.frequency,
                            payment_start_date.day
                        )
                cash_flows_list.append(cf)
            elif isinstance(s, SeriesCharge):
                if s.post_date_from is None and s.mode == Mode.ARREAR:
                    charge_start_date = roll_date(
                        charge_start_date,
                        s.frequency,
                        charge_start_date.day
                    )
                cf = s.to_cash_flows(charge_start_date
                                     if s.post_date_from is None
                                     else s.post_date_from)
                cf[Column.IS_CHARGE.value] = True
                if s.post_date_from is None:
                    # Updated only for system defined dates
                    charge_start_date = cf[Column.POST_DATE.value].iloc[-1]
                    if s.mode == Mode.ADVANCE:
                        # Shift date to end of last period
                        charge_start_date = roll_date(
                            charge_start_date,
                            s.frequency,
                            charge_start_date.day
                        )
                cash_flows_list.append(cf)

        if not cash_flows_list:
            # Handle empty case
            profile = pd.DataFrame(columns=[
                Column.POST_DATE.value,
                Column.VALUE_DATE.value,
                Column.AMOUNT.value,
                Column.IS_KNOWN.value,
                Column.WEIGHTING.value,
                Column.LABEL.value,
                Column.MODE.value,
                Column.IS_INTEREST_CAPITALISED.value,
                Column.IS_CHARGE.value
            ])
            return profile.astype({
                Column.POST_DATE.value: 'datetime64[ns, UTC]',
                Column.VALUE_DATE.value: 'datetime64[ns, UTC]',
                Column.AMOUNT.value: 'float64',
                Column.IS_KNOWN.value: 'bool',
                Column.WEIGHTING.value: 'float64',
                Column.LABEL.value: 'object',
                Column.MODE.value: 'object',
                Column.IS_INTEREST_CAPITALISED.value: 'object',
                Column.IS_CHARGE.value: 'bool'
            })

        profile = pd.concat(cash_flows_list, ignore_index=True)
        # Ensure consistent dtypes
        profile = profile.astype({
            Column.POST_DATE.value: 'datetime64[ns, UTC]',
            Column.VALUE_DATE.value: 'datetime64[ns, UTC]',
            Column.AMOUNT.value: 'float64',
            Column.IS_KNOWN.value: 'bool',
            Column.WEIGHTING.value: 'float64',
            Column.LABEL.value: 'object',
            Column.MODE.value: 'object',
            Column.IS_INTEREST_CAPITALISED.value: 'object', # Allow None
            Column.IS_CHARGE.value: 'bool'
        })
        return profile

    def _sort_cash_flows(self,
        cash_flows: pd.DataFrame,
        sort_by: SortColumn = SortColumn.POST_DATE) -> pd.DataFrame:
        """
        Sorts a cash flow DataFrame by date, object type, and optionally amount.

        Args:
            cash_flows (pd.DataFrame): DataFrame containing cash flow data with columns
                defined by CashFlowColumn.
            sort_by (SortColumn, optional): The column for the primary date sort.
                Options: SortColumn.POST_DATE (default), SortColumn.VALUE_DATE.

        Returns:
            pd.DataFrame: A new sorted DataFrame with rows ordered by:
                1. Specified date column (ascending, earliest first).
                2. Object type (Advance > Payment > Charge) for same-dated entries.
                3. Amount (descending, largest first) for same-dated entries of the same
                   type, only if all CashFlowColumn.IS_KNOWN values are True.

        Raises:
            ValidationError: If sort_by is not a valid SortColumn value.

        Notes:
            - Object type is determined by:
                - Advance: `CashFlowColumn.IS_CHARGE` is False and
                  `CashFlowColumn.IS_INTEREST_CAPITALISED` is None.
                - Payment: `CashFlowColumn.IS_CHARGE` is False and
                  `CashFlowColumn.IS_INTEREST_CAPITALISED` is not None.
                - Charge: `CashFlowColumn.IS_CHARGE` is True.
            - The amount sort is skipped if any `CashFlowColumn.IS_KNOWN` is False to avoid
              ordering based on placeholder values.
        """
        if cash_flows.empty:
            return cash_flows.copy()

        if not isinstance(sort_by, SortColumn):
            raise ValidationError(
                f"sort_by must be a SortColumn value: {[c.value for c in SortColumn]}"
            )

        # Create a copy to avoid modifying the input
        result = cash_flows.copy()

        # Create a column for object type sorting
        def get_object_type(row):
            if row[Column.IS_CHARGE.value]:
                return 2  # Charge
            if pd.notna(row[Column.IS_INTEREST_CAPITALISED.value]):
                return 1  # Payment
            return 0  # Advance

        result['object_type'] = result.apply(get_object_type, axis=1)

        # Determine if all amounts are known
        all_known = result[Column.IS_KNOWN.value].all()

        # Define sort columns
        sort_columns = [sort_by.value, 'object_type']
        ascending = [True, True]  # Ascending for date, ascending for object_type

        if all_known:
            # Include amount sort only if all amounts are known
            sort_columns.append(Column.AMOUNT.value)
            ascending.append(False)  # Descending for amount

        # Sort the DataFrame
        result = result.sort_values(
            by=sort_columns,
            ascending=ascending,
            ignore_index=True
        )

        # Drop the temporary object_type column
        result = result.drop(columns=['object_type'])
        return result

    def _validate_profile(
        self,
        df: pd.DataFrame,
        sort_by: SortColumn = SortColumn.POST_DATE,
        mode: ValidationMode = ValidationMode.SOLVE_VALUE
    ) -> None:
        """
        Validates the cash flow DataFrame for solving value or rate.

        Args:
            df: DataFrame containing cash flow data with columns defined by CashFlowColumn.
            sort_by: Expected sort column for the DataFrame (POST_DATE or VALUE_DATE).
            mode: Validation mode (SOLVE_VALUE or SOLVE_RATE).

        Raises:
            ValidationError: If validation fails (e.g., missing columns, invalid data,
            incorrect unknowns).
        """
        if df.empty:
            raise ValidationError("Cash flow DataFrame is empty")

        # Check required columns and dtypes
        required_columns = [col.value for col in Column]
        if not set(required_columns).issubset(df.columns):
            raise ValidationError(
                f"Missing required columns: {set(required_columns) - set(df.columns)}")

        expected_dtypes = {
            Column.POST_DATE.value: 'datetime64[ns, UTC]',
            Column.VALUE_DATE.value: 'datetime64[ns, UTC]',
            Column.AMOUNT.value: 'float64',
            Column.IS_KNOWN.value: 'bool',
            Column.WEIGHTING.value: 'float64',
            Column.LABEL.value: 'object',
            Column.MODE.value: 'object',
            Column.IS_INTEREST_CAPITALISED.value: 'object',  # Allows None
            Column.IS_CHARGE.value: 'bool'
        }
        for col, dtype in expected_dtypes.items():
            if col in df.columns and df[col].dtype != dtype:
                raise ValidationError(f"Column {col} must have dtype {dtype}, got {df[col].dtype}")

        # Check for NaN in required columns, excluding is_interest_capitalised
        strict_required_columns = [
            col for col in required_columns if col != Column.IS_INTEREST_CAPITALISED.value]
        if df[strict_required_columns].isna().any().any():
            raise ValidationError("Cash flow DataFrame contains NaN values in required columns")

        # Validate is_interest_capitalised
        payments = df[
            (~df[Column.IS_CHARGE.value]) & (df[Column.IS_INTEREST_CAPITALISED.value].notna())]
        non_payments = df[
            (df[Column.IS_CHARGE.value]) | (df[Column.IS_INTEREST_CAPITALISED.value].isna())]
        if not payments.empty:
            if payments[
                Column.IS_INTEREST_CAPITALISED.value
                ].apply(lambda x: x not in [True, False]).any():
                raise ValidationError("is_interest_capitalised must be True or False for payments")
        if not non_payments.empty:
            if non_payments[Column.IS_INTEREST_CAPITALISED.value].notna().any():
                raise ValidationError(
                    "is_interest_capitalised must be None for advances and charges")

        # Check weighting > 0
        if df[Column.WEIGHTING.value].le(0).any():
            raise ValidationError("Weighting must be > 0")

        # Check value_date >= post_date
        if (df[Column.VALUE_DATE.value] < df[Column.POST_DATE.value]).any():
            raise ValidationError("value_date must be on or after post_date")

        # Define advances, payments, and charges
        advances = df[
            (~df[Column.IS_CHARGE.value]) &
            (df[Column.IS_INTEREST_CAPITALISED.value].isna())
        ]
        payments = df[
            (~df[Column.IS_CHARGE.value]) &
            (df[Column.IS_INTEREST_CAPITALISED.value].notna())
        ]
        charges = df[df[Column.IS_CHARGE.value]]

        # Check at least one advance and one payment
        if advances.empty:
            raise ValidationError("At least one advance required")
        if payments.empty:
            raise ValidationError("At least one payment required")

        # Check payment/charge post_date >= earliest advance post_date
        earliest_advance_date = advances[Column.POST_DATE.value].min()
        non_advances = df[
            df[Column.IS_CHARGE.value] | df[Column.IS_INTEREST_CAPITALISED.value].notna()]
        if not non_advances.empty:
            if (non_advances[Column.POST_DATE.value] < earliest_advance_date).any():
                raise ValidationError(
                    "Payment or charge post_date cannot predate the earliest advance post_date"
                )

        # Check charges: non-negative and known
        if not charges.empty:
            if charges[Column.AMOUNT.value].lt(0).any():
                raise ValidationError("Charge amounts must be non-negative")
            if (~charges[Column.IS_KNOWN.value]).any():
                raise ValidationError("Charge values must be known")

        # Check last payment includes interest capitalization
        if not payments.empty:
            last_payment_date = payments[Column.POST_DATE.value].max()
            last_payments = payments[payments[Column.POST_DATE.value] == last_payment_date]
            if not last_payments[Column.IS_INTEREST_CAPITALISED.value].any():
                raise ValidationError(
                    "Interest and capital repayment cash flow end dates misaligned. "
                    "Check end dates."
                )

        # Check charges don’t postdate final payment
        if not charges.empty and not payments.empty:
            last_payment_date = payments[Column.POST_DATE.value].max()
            if (charges[Column.POST_DATE.value] > last_payment_date).any():
                raise ValidationError(
                    "Charge post_date cannot postdate the final payment post_date"
                )

        # Mode-specific validations
        unknowns = df[~df[Column.IS_KNOWN.value]]
        if mode == ValidationMode.SOLVE_VALUE:
            if unknowns.empty:
                raise ValidationError(
                    "At least one unknown advance or payment value required in SOLVE_VALUE mode"
                )
            if not unknowns[Column.AMOUNT.value].eq(0.0).all():
                raise ValidationError(
                    "Unknown values must be 0.0 (placeholder) in SOLVE_VALUE mode"
                )
            # Check unknowns are either all advances or all payments
            unknown_advances = unknowns[
                (~unknowns[Column.IS_CHARGE.value]) &
                (unknowns[Column.IS_INTEREST_CAPITALISED.value].isna())
            ]
            unknown_payments = unknowns[
                (~unknowns[Column.IS_CHARGE.value]) &
                (unknowns[Column.IS_INTEREST_CAPITALISED.value].notna())
            ]
            if not (unknown_advances.empty or unknown_payments.empty):
                raise ValidationError(
                    "Unknowns must be either all advances or all payments, not both"
                )
        elif mode == ValidationMode.SOLVE_RATE:
            if not unknowns.empty:
                raise ValidationError("All values must be known in SOLVE_RATE mode")

        # Check sort order
        if not df[sort_by.value].is_monotonic_increasing:
            raise ValidationError(
                f"Cash flows must be sorted by {sort_by.value} in ascending order"
            )

    def _assign_factors(self, cash_flows: pd.DataFrame, convention: Convention) -> pd.DataFrame:
        """
        Assigns time factors to the cash flow DataFrame based on the day count convention.

        Args:
            cash_flows (pd.DataFrame): DataFrame containing cash flow data with
                CashFlowColumn.POST_DATE and CashFlowColumn.VALUE_DATE.
            convention (Convention): The day count convention for computing time intervals.

        Returns:
            pd.DataFrame: A copy of the input DataFrame with an added 'factor' column
                containing computed DayCountFactor objects.

        Notes:
            - Factors are computed from the first advance's post_date or value_date (if
              DayCountOrigin.DRAWDOWN) or between consecutive dates (if DayCountOrigin.NEIGHBOUR).
            - For charges, if include_non_financing_flows is False, the factor is computed
              between the same date (zero period).
            - The date used (post_date or value_date) depends on convention.use_post_dates.
        """
        cash_flows = cash_flows.copy()
        date_column = (
            Column.POST_DATE.value
            if convention.use_post_dates
            else Column.VALUE_DATE.value
        )

        # Initialize the factor column as object type to store DayCountFactor
        cash_flows[ColumnExtras.FACTOR.value] = None

        # Find the first advance's date for DRAWDOWN origin
        advances = cash_flows[
            (~cash_flows[Column.IS_CHARGE.value]) &
            (cash_flows[Column.IS_INTEREST_CAPITALISED.value].isna())
        ]
        if advances.empty:
            raise ValidationError("At least one advance required for factor assignment")
        drawdown_date = advances[date_column].min()

        # For NEIGHBOUR origin, track the previous date
        neighbour_date = drawdown_date

        for idx in cash_flows.index:
            cash_flow_date = cash_flows.loc[idx, date_column]
            is_charge = cash_flows.loc[idx, Column.IS_CHARGE.value]

            # Handle charges when non-financing flows are excluded
            if is_charge and not convention.include_non_financing_flows:
                factor = convention.compute_factor(cash_flow_date, cash_flow_date)
                cash_flows.at[idx, ColumnExtras.FACTOR.value] = factor
                continue

            # Handle cash flows predating or equal to drawdown_date
            if cash_flow_date <= drawdown_date:
                factor = convention.compute_factor(cash_flow_date, cash_flow_date)
            else:
                if convention.day_count_origin == DayCountOrigin.DRAWDOWN:
                    factor = convention.compute_factor(drawdown_date, cash_flow_date)
                else:  # NEIGHBOUR
                    factor = convention.compute_factor(neighbour_date, cash_flow_date)
                    neighbour_date = cash_flow_date

            cash_flows.at[idx, ColumnExtras.FACTOR.value] = factor

        return cash_flows

    def _calculate_nfv(
        self,
        cash_flows: pd.DataFrame,
        convention: Convention,
        interest_rate: float) -> float:
        """
        Calculates the net future value (NFV) of the cash flow profile.

        Args:
            cash_flows (pd.DataFrame): DataFrame with CashFlowColumn columns and a 'factor'
                column from _assign_factors.
            convention (Convention): The day count convention for interest calculations.
            interest_rate (float): The annual effective interest rate as a decimal, except 
                when using the USAppendixJ day count convention where the rate is the periodic
                effective interest rate (e.g., annual rate / 12 for monthly periods).
        Returns:
            float: The net future value of the cash flows at the final date.

        Notes:
            - Excludes charges if `convention.include_non_financing_flows` is False.
            - Handles interest capitalization for payments based on
              `CashFlowColumn.IS_INTEREST_CAPITALISED`.
            - For USAppendixJ, applies fractional and principal factor adjustments.
            - Uses `post_date` or `value_date` based on `convention.use_post_dates`.
        """
        capital_balance = 0.0

        if convention.day_count_origin == DayCountOrigin.DRAWDOWN:
            for _, row in cash_flows.iterrows():
                if (row.get(Column.IS_CHARGE.value, False) and not
                    convention.include_non_financing_flows):
                    continue
                factor = row[ColumnExtras.FACTOR.value]
                amount = row[Column.AMOUNT.value] or 0.0

                if isinstance(convention, USAppendixJ):
                    primary_period_factor = (1 + interest_rate) ** factor.primary_period_fraction
                    partial_period_factor = (
                        1.0 + (factor.partial_period_fraction * interest_rate)
                        if (factor.partial_period_fraction is not None and
                            factor.partial_period_fraction / 12.0 > 0.0)
                        else 1.0
                    )
                    capital_balance += amount / (primary_period_factor * partial_period_factor)
                else:
                    capital_balance += amount * (1 + interest_rate) ** (-factor.primary_period_fraction)
        else:  # NEIGHBOUR
            accrued_interest = 0.0
            for _, row in cash_flows.iterrows():
                if (row.get(Column.IS_CHARGE.value, False) and not
                    convention.include_non_financing_flows):
                    continue
                factor = row[ColumnExtras.FACTOR.value]
                amount = row[Column.AMOUNT.value] or 0.0
                is_payment = row[Column.IS_INTEREST_CAPITALISED.value] is not None
                period_interest = capital_balance * interest_rate * factor.primary_period_fraction

                if is_payment:
                    if row[Column.IS_INTEREST_CAPITALISED.value]:
                        capital_balance += accrued_interest + period_interest + amount
                        accrued_interest = 0.0
                    else:
                        accrued_interest += period_interest
                        capital_balance += amount
                else:
                    capital_balance += period_interest + amount

        return capital_balance

    def _update_unknowns(
        self,
        cash_flows: pd.DataFrame,
        value: float,
        precision: int = 2,
        is_rounded: bool = False) -> pd.DataFrame:
        """
        Updates the amounts of unknown cash flows in the DataFrame.

        Args:
            cash_flows (pd.DataFrame): DataFrame with CashFlowColumn columns, including 
                'amount', 'is_known', and 'weighting'.
            value (float): The base amount to assign to unknown cash flows, adjusted
                by weighting.
            precision (int): Number of decimal places for rounding (default: 2).
            is_rounded (bool): Whether to round the adjusted amounts (default: False).

        Returns:
            pd.DataFrame: A copy of the input DataFrame with updated 'amount' for unknown
            cash flows.

        Notes:
            - Unknown cash flows are those with `is_known=False`.
            - Each unknown cash flow's amount is set to `value * weighting`
              (rounded if is_rounded=True).
            - The `is_known` column is not modified to preserve identification of computed amounts.
            - If no unknown cash flows exist, the DataFrame is returned unchanged.
        """
        cash_flows = cash_flows.copy()

        # Identify unknown cash flows
        mask = cash_flows[Column.IS_KNOWN.value] == False # pylint: disable=C0121:singleton-comparison

        if not mask.any():
            return cash_flows

        # Compute adjusted values: value * weighting
        adjusted_values = cash_flows[mask][Column.WEIGHTING.value] * value

        # Apply rounding if requested
        if is_rounded:
            adjusted_values = adjusted_values.apply(lambda x: gauss_round(x, precision))

        # Update amounts for unknown cash flows
        cash_flows.loc[mask, Column.AMOUNT.value] = adjusted_values

        return cash_flows

    def _amortise_interest(
        self,
        cash_flows: pd.DataFrame,
        interest_rate: float,
        precision: int = 2) -> pd.DataFrame:
        """
        Updates the amortised interest amounts for payment cash flows in an amortization schedule.

        Adds an 'interest' column (float64) to the DataFrame, representing the interest portion
        of each payment's amount, with the capital portion being amount - interest. Interest is
        negative for capitalized payments due to a negative capital balance from advances.
        The final payment's interest is adjusted to offset the capital balance, absorbing
        rounding errors.

        Args:
            cash_flows (pd.DataFrame): DataFrame with CashFlowColumn columns, including 'amount',
                'factor', 'is_charge', 'is_interest_capitalised', and optionally 'interest'.
            interest_rate (float): Annual effective interest rate (e.g., 0.12 for 12%).
            precision (int): Number of decimal places for rounding (default: 2).

        Returns:
            pd.DataFrame: A copy of the input DataFrame with an 'interest' column (float64) 
            for payments.
        """
        cash_flows = cash_flows.copy()
        cash_flows[
            ColumnExtras.INTEREST.value
            ] = pd.Series(0.0, dtype='float64', index=cash_flows.index)

        capital_balance = 0.0
        accrued_interest = 0.0

        for idx, row in cash_flows.iterrows():
            if row.get(Column.IS_CHARGE.value, False):
                continue

            factor = row[ColumnExtras.FACTOR.value].primary_period_fraction
            amount = row[Column.AMOUNT.value] or 0.0
            period_interest = gauss_round(capital_balance * interest_rate * factor, precision)

            if row.get(Column.IS_INTEREST_CAPITALISED.value) is not None:  # Payment
                if row[Column.IS_INTEREST_CAPITALISED.value]:
                    interest = gauss_round(accrued_interest + period_interest, precision)
                    capital_balance += interest + amount
                    accrued_interest = 0.0
                else:
                    interest = 0.0
                    accrued_interest += period_interest
                    capital_balance += amount
                cash_flows.at[idx, ColumnExtras.INTEREST.value] = interest
            else:  # Advance
                accrued_interest += period_interest
                capital_balance -= period_interest  # Feb 2025 fix: avoid double-counting
                capital_balance += period_interest + amount

        # Adjust the last payment's interest to offset capital_balance
        payment_indices = cash_flows[
            cash_flows[Column.IS_INTEREST_CAPITALISED.value].notna()
        ].index
        if not payment_indices.empty:
            last_payment_idx = payment_indices[-1]
            current_interest = cash_flows.at[last_payment_idx, ColumnExtras.INTEREST.value]
            cash_flows.at[last_payment_idx, ColumnExtras.INTEREST.value] = gauss_round(
                current_interest - capital_balance, precision
            )

        return cash_flows
