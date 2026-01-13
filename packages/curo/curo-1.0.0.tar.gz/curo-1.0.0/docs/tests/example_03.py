# tests/example_03.py
# pylint: disable=C0301:line-too-long
"""
Example 3: Solve Unknown Payment with Irregular Interest Compounding

Add content here... needs date input

>>> import pandas as pd
>>> from curo import (
...     Calculator, Frequency,
...     SeriesAdvance, SeriesPayment,
...     US30U360
... )
...  
... # Step 1: Create a [Calculator](api/calculator.md) instance
>>> calculator = Calculator()
... 
... # Step 2: Define cash flow series
>>> calculator.add(
...     SeriesAdvance(
...         label="Loan",
...         amount=10000.0,
...         post_date_from = pd.Timestamp("2026-01-05", tz="UTC")
...     )
... )
>>> calculator.add(  # Payment (capital-only) series
...     SeriesPayment(
...         number_of = 6,
...         label = "Instalment",
...         amount = None,
...         frequency = Frequency.MONTHLY,
...         post_date_from = pd.Timestamp("2026-2-05", tz="UTC"),
...         is_interest_capitalised = False  # No interest
...     )
... )
>>> calculator.add(  # Interest-only series
...     SeriesPayment(
...         number_of = 2,
...         label = "Interest",
...         amount = 0.0,  # Zero payment value (interest only)
...         frequency = Frequency.QUARTERLY,
...         post_date_from = pd.Timestamp("2026-04-05", tz="UTC"),
...         is_interest_capitalised = True  # Add interest
...     )
... )
...
... # Step 3: Solve for the unknown and validate rate
>>> payment = calculator.solve_value(
...     convention = US30U360(),
...     interest_rate = 0.0825,
...     start_date = pd.Timestamp("2026-01-05", tz="UTC")
... )
>>> irr = calculator.solve_rate(
...     convention = US30U360()
... )
>>> amortisation_schedule = calculator.build_schedule(
...     profile = calculator.profile,
...     convention = US30U360(),
...     interest_rate = irr
... )
>>> amortisation_schedule['post_date'] = amortisation_schedule['post_date'].dt.strftime('%Y-%m-%d')
... 
... # Step 4: Display results and schedule
>>> print(f"Monthly instalment: ${payment:.2f}")
Monthly instalment: $1706.67
>>> print(f"Implicit interest rate: {irr:.2%}")
Implicit interest rate: 8.25%
>>> print(amortisation_schedule)
    post_date       label    amount   capital  interest  capital_balance
0  2026-01-05        Loan -10000.00 -10000.00      0.00        -10000.00
1  2026-02-05  Instalment   1706.67   1706.67      0.00         -8293.33
2  2026-03-05  Instalment   1706.67   1706.67      0.00         -6586.66
3  2026-04-05  Instalment   1706.67   1706.67      0.00         -4879.99
4  2026-04-05    Interest      0.00   -171.04   -171.04         -5051.03
5  2026-05-05  Instalment   1706.67   1706.67      0.00         -3344.36
6  2026-06-05  Instalment   1706.67   1706.67      0.00         -1637.69
7  2026-07-05  Instalment   1706.67   1706.67      0.00            68.98
8  2026-07-05    Interest      0.00    -68.98    -68.98             0.00
"""
