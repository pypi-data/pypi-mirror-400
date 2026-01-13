"""
Curo Python is a powerful, open-source library for performing instalment credit
financial calculations, from simple loans to complex leasing and hire purchase
agreements. Built from the ground up in Python, it leverages pandas DataFrames
for cash flow management and SciPy for efficient solving of unknown values or
rates using Brent's method.
"""

__author__ = "Andrew Murphy"
__email__ = "curocalculator@gmail.com"
import importlib.metadata
__version__ = importlib.metadata.version("curo")

# Expose public API classes and enums
from .calculator import Calculator
from .daycount.actual_360 import Actual360
from .daycount.actual_365 import Actual365
from .daycount.actual_isda import ActualISDA
from .daycount.day_count_factor import DayCountFactor
from .daycount.eu_30_360 import EU30360
from .daycount.eu_2008_48 import EU200848EC
from .daycount.uk_conc_app import UKConcApp
from .daycount.us_30_360 import US30360
from .daycount.us_30u_360 import US30U360
from .daycount.us_appendix_j import USAppendixJ
from .enums import CashFlowColumn, DayCountTimePeriod, Frequency, Mode
from .exceptions import UnsolvableError, ValidationError
from .series import SeriesAdvance, SeriesPayment, SeriesCharge

# Define what gets exported with `from curo import *`
__all__ = [
    "Calculator",
    "Actual360",
    "Actual365",
    "ActualISDA",
    "CashFlowColumn",
    "DayCountFactor",
    "DayCountTimePeriod",
    "EU30360",
    "EU200848EC",
    "Frequency",
    "Mode",
    "SeriesAdvance",
    "SeriesPayment",
    "SeriesCharge",
    "UKConcApp",
    "UnsolvableError",
    "US30360",
    "US30U360",
    "USAppendixJ",
    "ValidationError",
    "__version__",
]
