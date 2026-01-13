"""
Module defining enums for financial calculations and cash flow modeling in the library.
"""

from enum import Enum

class Frequency(Enum):
    """
    Enum defining the compounding period between cash flows.

    Attributes:
        WEEKLY: Weekly compounding period.
        FORTNIGHTLY: Biweekly (every two weeks) compounding period.
        MONTHLY: Monthly compounding period.
        QUARTERLY: Quarterly (every three months) compounding period.
        HALF_YEARLY: Semi-annual (every six months) compounding period.
        YEARLY: Annual compounding period.
    """
    WEEKLY = "weekly"
    FORTNIGHTLY = "fortnightly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    HALF_YEARLY = "half_yearly"
    YEARLY = "yearly"

    @property
    def pandas_freq(self) -> str:
        """
        Maps the frequency to a pandas frequency alias for time series operations.

        Returns:
            str: Pandas frequency alias (e.g., "W" for WEEKLY, "ME" for MONTHLY).
        """
        return {
            "weekly": "W",
            "fortnightly": "2W",
            "monthly": "ME",
            "quarterly": "QE",
            "half_yearly": "6ME",
            "yearly": "YE"
        }[self.value]

class Mode(Enum):
    """
    Enum specifying whether a cash flow occurs at the start or end of a compounding period.

    Attributes:
        ADVANCE: Cash flows due at the beginning of the compounding period.
        ARREAR: Cash flows due at the end of the compounding period.
    """
    ADVANCE = "advance"
    ARREAR = "arrear"

class DayCountTimePeriod(Enum):
    """
    Enum defining the time interval for day count factor calculations in financial computations.

    Attributes:
        DAY: Daily interval.
        WEEK: Weekly interval.
        FORTNIGHT: Biweekly (every two weeks) interval.
        MONTH: Monthly interval.
        QUARTER: Quarterly (every three months) interval.
        HALF_YEAR: Semi-annual (every six months) interval.
        YEAR: Annual interval.
    """
    DAY = "day"
    WEEK = "week"
    FORTNIGHT = "fortnight"
    MONTH = "month"
    QUARTER = "quarter"
    HALF_YEAR = "half_year"
    YEAR = "year"

    @property
    def periods_in_year(self) -> int:
        """
        Maps the time period to the number of such periods in a year for financial calculations.

        Returns:
            int: Number of periods in a year (e.g., 365 for DAY, 12 for MONTH).
        """
        return {
            "day": 365,
            "week": 52,
            "fortnight": 26,
            "month": 12,
            "quarter": 4,
            "half_year": 2,
            "year": 1
        }[self.value]

class DayCountOrigin(Enum):
    """
    Enum used internally to define the start date for calculating day counts
    in financial time periods.

    Attributes:
        DRAWDOWN: The initial drawdown post date, used in APR and XIRR calculations.
        NEIGHBOUR: A neighboring cash flow date, used for compounding periods in solving
            unknown values or effective interest rates.
    """
    DRAWDOWN = "drawdown"
    NEIGHBOUR = "neighbour"

class CashFlowColumn(Enum):
    """
    Enum defining the mandatory column names for pandas DataFrames used in cash flow
    calculations within the Calculator class.

    These columns are required in all cash flow profiles, whether created internally
    (e.g., via Calculator._build_profile) or provided as bespoke profiles by users.
    They represent the core attributes of cash flows used in methods like solve_rate,
    solve_value, and build_schedule.

    Attributes:
        POST_DATE (str): The posting date of the cash flow (datetime64[ns, UTC]).
            Typically when the cash flow is recorded or effective.
        VALUE_DATE (str): The value date of the cash flow (datetime64[ns, UTC]).
            Represents when the cash flow impacts the balance, must be on or after POST_DATE.
        AMOUNT (str): The cash flow amount (float64). Negative for advances, positive for
            payments and charges. Unknown amounts use 0.0 as a placeholder with IS_KNOWN=False.
        IS_KNOWN (str): Indicates if the AMOUNT is known (bool). True for user-provided or
            calculated amounts, False for unknowns to be solved (e.g., in solve_value).
        WEIGHTING (str): The weighting factor for the cash flow (float64). Must be > 0, used
            to scale amounts in solve_value calculations.
        LABEL (str): A descriptive label for the cash flow (object). E.g., 'Loan', 'Instalment'.
        MODE (str): The cash flow mode (object). Either 'advance' or 'arrear', defining
            timing relative to periods.
        IS_INTEREST_CAPITALISED (str): Indicates if the payment includes interest
            capitalization (object). True/False for payments, None for advances/charges.
        IS_CHARGE (str): Indicates if the cash flow is a charge (bool). True for charges,
            False for advances/payments.
    """
    POST_DATE = "post_date"
    VALUE_DATE = "value_date"
    AMOUNT = "amount"
    IS_KNOWN = "is_known"
    WEIGHTING = "weighting"
    LABEL = "label"
    MODE = "mode"
    IS_INTEREST_CAPITALISED = "is_interest_capitalised"
    IS_CHARGE = "is_charge"

class CashFlowColumnExtras(Enum):
    """
    Enum defining supplemental column names added to pandas DataFrames in result outputs
    generated by the Calculator class, such as Amortization or APR proof schedules.

    These columns are not part of input cash flow profiles but are added during processing
    by methods like build_schedule. The specific columns included depend on the schedule
    type: Amortization (capital, interest, capital_balance) or APR proof (discount_log,
    amount_discounted, discounted_balance). The 'factor' column is required in input
    profiles for build_schedule, typically added via _assign_factors.

    Attributes:
        AMOUNT_DISCOUNTED (str): The discounted cash flow amount (float64) in APR proof
            schedules, rounded to 6 decimal places.
        CAPITAL (str): The capital portion of a payment (float64) in Amortization schedules,
            calculated as amount - interest.
        CAPITAL_BALANCE (str): The running capital balance (float64) in Amortization
            schedules, netting to zero at the end.
        DISCOUNT_LOG (str): A string representation of the discount factor (object) in APR
            proof schedules, derived from factor.to_folded_string().
        DISCOUNTED_BALANCE (str): The cumulative sum of amount_discounted (float64) in APR
            proof schedules, netting to zero, rounded to 6 decimal places.
        FACTOR (str): The day count factor (object) for cash flows, containing
            DayCountFactor objects. Required in input profiles for build_schedule.
        INTEREST (str): The interest portion of a payment (float64) in Amortization
            schedules, negative for capitalized payments.
    """
    AMOUNT_DISCOUNTED = "amount_discounted"
    CAPITAL = "capital"
    CAPITAL_BALANCE = "capital_balance"
    DISCOUNT_LOG = "discount_log"
    DISCOUNTED_BALANCE = "discounted_balance"
    FACTOR = "factor"
    INTEREST = "interest"

class SortColumn(Enum):
    """
    Enum used internally to define the date sort order of pandas DataFrame cashflow entries.
    """
    POST_DATE = CashFlowColumn.POST_DATE.value
    VALUE_DATE = CashFlowColumn.VALUE_DATE.value

class ValidationMode(Enum):
    """
    Enum used internally to define the validation mode when solving for an unknown 
    value or interest rate.
    
    Attributes:
        SOLVE_VALUE: Allows undefined advance OR payment values
        SOLVE_RATE: Requires all values to be known
    """
    SOLVE_VALUE = "solve_value"
    SOLVE_RATE = "solve_rate"
