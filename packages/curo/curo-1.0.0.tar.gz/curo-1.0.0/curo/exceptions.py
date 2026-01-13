"""
Module defining validation and unsolvable error conditions.
"""

class ValidationError(ValueError):
    """
    Raised when a cash flow profile or input is invalid.
    """
    pass

class UnsolvableError(RuntimeError):
    """
    Raised when a numerical solver fails to converge on a solution.
    """
    pass
