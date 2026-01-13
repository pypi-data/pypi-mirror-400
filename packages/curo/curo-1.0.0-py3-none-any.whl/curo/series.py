"""
Module provides type-safe classes for capturing user-defined advance,
payment, and charge series input.
"""

from dataclasses import dataclass
from typing import Optional, Union
from datetime import datetime
import pandas as pd
from curo.enums import CashFlowColumn as Column, Frequency, Mode
from curo.exceptions import ValidationError
from curo.utils import has_month_end_day, to_timestamp

@dataclass
class Series:
    """
    Abstract base class for financial series (advances, payments, charges).

    Defines common properties and a method to convert the series into a pandas DataFrame
    of dated cash flow data. Inherited by `SeriesAdvance`, `SeriesPayment`, and `SeriesCharge`.

    Args:
        number_of: Total number of cash flows in the series. Must be >= 1. Defaults to 1.
        frequency: Frequency of recurring cash flows (e.g., `Frequency.MONTHLY`).
            Defaults to `Frequency.MONTHLY`.
        label: Descriptive label for cash flows (e.g., "Loan advance"). Defaults to an empty string.
        amount: Cash flow value. If `None`, treated as unknown for solving (except for charges).
            Defaults to `None`.
        mode: Mode of cash flows (`Mode.ADVANCE` or `Mode.ARREAR`). Defaults to `Mode.ADVANCE`.
        post_date_from: Start date for postings. Converted to a UTC `pd.Timestamp` at midnight.
            Defaults to `None`.
        value_date_from: Start date for value/settlement, on or after `post_date_from` (only for
            advances). Converted to a UTC `pd.Timestamp` at midnight. Defaults to `None`.
        weighting: Weighting for unknown values. Must be positive. Defaults to 1.0.

    Raises:
        ValidationError:
            - If `number_of` is less than 1.
            - If `weighting` is less than or equal to 0.
            - If `value_date_from` is set but `post_date_from` is not (for advances).
            - If `value_date_from` is earlier than `post_date_from` (for advances).

    Notes:
        - Dates are normalized to midnight UTC.
        - `value_date_from` is only allowed for `SeriesAdvance` and is set to `post_date_from`
          if `None` when required.
    """
    number_of: int = 1
    frequency: Frequency = Frequency.MONTHLY
    label: str = ''
    amount: Optional[float] = None
    mode: Mode = Mode.ADVANCE
    post_date_from: Optional[Union[pd.Timestamp, datetime, datetime.date]] = None
    value_date_from: Optional[Union[pd.Timestamp, datetime, datetime.date]] = None
    weighting: float = 1.0

    def __post_init__(self):
        # Convert dates to pd.Timestamp (midnight UTC)
        self.post_date_from = to_timestamp(self.post_date_from)
        self.value_date_from = to_timestamp(self.value_date_from)

        # Validation
        if self.number_of < 1:
            raise ValidationError("number_of must be >= 1")
        if self.weighting <= 0:
            raise ValidationError("weighting must be > 0")
        if self.post_date_from is None and self.value_date_from is not None:
            raise ValidationError("post_date_from required when value_date_from is set")
        if (self.post_date_from is not None and
            self.value_date_from is not None and
            self.value_date_from < self.post_date_from):
            raise ValidationError("value_date_from must be on or after post_date_from")
        if self.post_date_from is not None and self.value_date_from is None:
            self.value_date_from = self.post_date_from

    def to_cash_flows(self,
                      start_date: Union[pd.Timestamp, datetime, datetime.date]) -> pd.DataFrame:
        """
        Converts the series into a pandas DataFrame containing dated cash flow data.

        Generates a sequence of cash flows based on the series' properties, including
        posting and value dates, amounts, and other attributes. Dates are normalized to
        midnight UTC, and the frequency determines the interval between cash flows.

        Args:
            start_date: The reference start date for the series, normalized to midnight UTC.

        Returns:
            A pandas DataFrame with columns:
            - post_date: Posting dates of the cash flows (UTC).
            - value_date: Value or settlement dates of the cash flows (UTC).
            - amount: Cash flow amounts (or None if unknown).
            - is_known: Boolean indicating if the amount is specified.
            - weighting: Weighting factor for the cash flow.
            - label: Descriptive label for the cash flow.
            - mode: The mode of the cash flow (e.g., ADVANCE or ARREAR).
            - is_interest_capitalised: Boolean indicating if interest compounds with the
                payment frequency (True for SeriesPayment with is_interest_capitalised=True,
                None for other series).

        Notes:
            - Dates are adjusted to preserve the day of the month from the start date,
                capped at the last day of the month if necessary.
            - The frequency determines the interval between cash flows (e.g., weekly, monthly).
            - For `SeriesCharge` and `SeriesPayment`, `value_date` matches `post_date` in the
                output DataFrame, ensuring consistent sorting by either column.
            - The `amount` column is set to `0.0` for unknown values (`self.amount is None`),
                with `is_known=False`. The `amount` placeholder is intended to be overridden
                by the solver.
        """

        # Determine start date
        if self.post_date_from:
            start = self.post_date_from
        else:
            start = to_timestamp(start_date)

        # Generate dates
        freq_map = {
            Frequency.WEEKLY: pd.offsets.Week(1),
            Frequency.FORTNIGHTLY: pd.offsets.Week(2),
            Frequency.MONTHLY: pd.offsets.DateOffset(months=1),
            Frequency.QUARTERLY: pd.offsets.DateOffset(months=3),
            Frequency.HALF_YEARLY: pd.offsets.DateOffset(months=6),
            Frequency.YEARLY: pd.offsets.DateOffset(years=1)
        }

        post_day = start.day
        if ((self.frequency != Frequency.WEEKLY or
            self.frequency != Frequency.QUARTERLY) and
            has_month_end_day(start)):
            # Coerce dates to use last day of month when a
            # series start date falls on a month-end
            post_day = 31

        if self.number_of == 1:
            dates = pd.Index([start])
        else:
            dates = pd.date_range(
                start=start,
                periods=self.number_of,
                freq=freq_map[self.frequency]
            )
            # Adjust to preserve start.day, capped at month-end
            dates = dates.map(
                lambda d: d.replace(day=min(post_day, pd.offsets.MonthEnd(0).rollforward(d).day))
            )
            dates = dates.floor('D').tz_convert('UTC')

        # Generate value_dates
        value_start = self.value_date_from or start
        value_day = value_start.day
        if ((self.frequency != Frequency.WEEKLY or
            self.frequency != Frequency.QUARTERLY) and
            has_month_end_day(value_start)):
            # Coerce dates to use last day of month when a
            # series start date falls on a month-end
            value_day = 31

        if self.number_of == 1:
            value_dates = pd.Index([value_start])
        else:
            value_dates = pd.date_range(
                start=value_start,
                periods=self.number_of,
                freq=freq_map[self.frequency]
            )
            # Adjust to preserve value_start.day, capped at month-end
            value_dates = value_dates.map(
                lambda d: d.replace(day=min(value_day, pd.offsets.MonthEnd(0).rollforward(d).day))
            )
            value_dates = value_dates.floor('D').tz_convert('UTC')

        # Determine is_interest_capitalised value
        is_interest_capitalised = (
            getattr(self, Column.IS_INTEREST_CAPITALISED.value, None)
            if isinstance(self, SeriesPayment)
            else None
        )
        return pd.DataFrame({
            Column.POST_DATE.value: dates,
            Column.VALUE_DATE.value: value_dates,
            Column.AMOUNT.value: [self.amount if self.amount is not None else 0.0] * self.number_of,
            Column.IS_KNOWN.value: [self.amount is not None] * self.number_of,
            Column.WEIGHTING.value: [self.weighting] * self.number_of,
            Column.LABEL.value: [self.label] * self.number_of,
            Column.MODE.value: [self.mode.value] * self.number_of,
            Column.IS_INTEREST_CAPITALISED.value: [is_interest_capitalised] * self.number_of
        })

@dataclass
class SeriesAdvance(Series):
    """
    Represents a series of one or more advances paid out by a lender, such as loans
    or a lessor's net investment in a lease.

    Args:
        number_of: Total number of advances in the series. Defaults to 1.
        frequency: Frequency of recurring advances (e.g., `Frequency.MONTHLY`).
            Defaults to `Frequency.MONTHLY`.
        label: Singular label for each cash flow (e.g., "Loan advance") for use in
            amortisation schedules or proofs. Defaults to an empty string.
        amount: Value of the advances. If `None`, treated as the unknown to solve for.
            Defaults to `None`.
        post_date_from: Posting or drawdown date of the first advance. Subsequent
            dates follow the series' `frequency`. If `None`, derived from the system
            date or a preceding series' end date. Defaults to `None`.
        value_date_from: Value or settlement date of the first advance, on or after
            `post_date_from`. If `None`, matches `post_date_from`. Used for deferred
            settlement schemes. Defaults to `None`.
        mode: Mode of advances (`Mode.ADVANCE` or `Mode.ARREAR`). Defaults to
            `Mode.ADVANCE`.
        weighting: Weighting of unknown advance values relative to other unknown
            series. Must be positive. Defaults to 1.0.

    Raises:
        ValidationError: Inherited from `Series` (e.g., invalid `number_of`, `weighting`,
            `post_date_from`, or `value_date_from`).
    """
    pass

@dataclass
class SeriesPayment(Series):
    """
    Represents a series of one or more payments received by a lender, such as loan
    repayments or lease rentals.

    Args:
        number_of: Total number of payments in the series. Defaults to 1.
        frequency: Frequency of recurring payments (e.g., `Frequency.MONTHLY`).
            Defaults to `Frequency.MONTHLY`.
        label: Singular label for each cash flow (e.g., "Rental") for use in
            amortisation schedules or proofs. Defaults to an empty string.
        amount: Value of the payments. If `None`, treated as the unknown to solve for.
            Defaults to `None`.
        post_date_from: Due date of the first payment. Subsequent dates follow the
            series' `frequency`. If `None`, derived from the system date or a preceding
            series' end date. Defaults to `None`.
        mode: Mode of payments (`Mode.ADVANCE` or `Mode.ARREAR`). Defaults to
            `Mode.ADVANCE`.
        weighting: Weighting of unknown payment values relative to other unknown
            series. Must be positive. Defaults to 1.0.
        is_interest_capitalised: If `True`, interest compounds with the payment
            frequency; if `False`, interest may compound at a different frequency
            (e.g., monthly payments with quarterly interest). Defaults to `True`.

    Raises:
        ValidationError:
            - If `value_date_from` is explicitly defined (not allowed for `SeriesPayment`).
            - Inherited from `Series` (e.g., invalid `number_of`, `weighting`, or `post_date_from`).
    """
    is_interest_capitalised: bool = True

    def __init__(
        self,
        number_of: int = 1,
        frequency: Frequency = Frequency.MONTHLY,
        label: str = '',
        amount: Optional[float] = None,
        mode: Mode = Mode.ADVANCE,
        post_date_from: Optional[Union[pd.Timestamp, datetime, datetime.date]] = None,
        value_date_from: Optional[Union[pd.Timestamp, datetime, datetime.date]] = None,
        weighting: float = 1.0,
        is_interest_capitalised: bool = True
    ):
        if value_date_from is not None:
            raise ValidationError("value_date_from must not be defined for SeriesPayment")
        super().__init__(
            number_of=number_of,
            frequency=frequency,
            label=label,
            amount=amount,
            mode=mode,
            post_date_from=post_date_from,
            value_date_from=None,  # Explicitly pass None
            weighting=weighting
        )
        self.is_interest_capitalised = is_interest_capitalised

@dataclass
class SeriesCharge(Series):
    """
    A series of one or more charges or fees received by a lender, such as
    arrangement fees. These non-financing cash flows are excluded from unknown advance
    or payment calculations but may be included in computations like Annual Percentage
    Rates (APRs).

    Args:
        number_of: Total number of charges in the series. Defaults to 1.
        frequency: Frequency of recurring charges (e.g., `Frequency.MONTHLY`).
            Defaults to `Frequency.MONTHLY`.
        label: Singular label for each cash flow (e.g., "Arrangement fee") for use in
            amortisation schedules or proofs. Defaults to an empty string.
        amount: Value of the charges (required).
        post_date_from: Due date of the first charge. Subsequent dates follow the
            series' `frequency`. If `None`, derived from the system date or a preceding
            series' end date. Defaults to `None`.
        mode: Mode of charges (`Mode.ADVANCE` or `Mode.ARREAR`). Defaults to
            `Mode.ADVANCE`.

    Raises:
        ValidationError:
            - If `amount` is `None` (required for `SeriesCharge`).
            - If `value_date_from` is explicitly defined (not allowed for `SeriesCharge`).
            - Inherited from `Series` (e.g., invalid `number_of`, `weighting`, or `post_date_from`).
    """
    amount: float  # Required

    def __init__(
        self,
        number_of: int = 1,
        frequency: Frequency = Frequency.MONTHLY,
        label: str = '',
        amount: float = None,
        mode: Mode = Mode.ADVANCE,
        post_date_from: Optional[Union[pd.Timestamp, datetime, datetime.date]] = None,
        value_date_from: Optional[Union[pd.Timestamp, datetime, datetime.date]] = None,
        weighting: float = 1.0
    ):
        if amount is None:
            raise ValidationError("amount is required for SeriesCharge")
        if value_date_from is not None:
            raise ValidationError("value_date_from must not be defined for SeriesCharge")
        super().__init__(
            number_of=number_of,
            frequency=frequency,
            label=label,
            amount=amount,
            mode=mode,
            post_date_from=post_date_from,
            value_date_from=None,  # Explicitly pass None
            weighting=weighting
        )
