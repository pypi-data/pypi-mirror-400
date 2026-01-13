# tests/example_04.py
# pylint: disable=C0301:line-too-long
"""
Example 4: Compute Supplier Contribution, 0% Interest Finance Promotion
and incorporating a 30 Day Deferred Settlement.

Add content here... needs date input

>>> import pandas as pd
>>> from curo import (
...     Calculator,
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
...         label="Cost of car",
...         amount=10000.0,
...         post_date_from = pd.Timestamp("2026-01-05", tz="UTC"),
...         value_date_from = pd.Timestamp("2026-02-05", tz="UTC")
...     )
... )
>>> calculator.add(
...     SeriesPayment(
...         label = "Deposit",
...         amount = 4000.0,
...         post_date_from = pd.Timestamp("2026-01-05", tz="UTC"),
...     )
... )
>>> calculator.add(
...     SeriesPayment(
...         label = "Supplier contribution",
...         amount = None,
...         post_date_from = pd.Timestamp("2026-2-05", tz="UTC"),
...     )
... )
>>> calculator.add(
...     SeriesPayment(
...         number_of = 6,
...         label = "Instalment",
...         amount = 1000.0,
...         post_date_from = pd.Timestamp("2026-02-05", tz="UTC")
...     )
... )
...
... # Step 3: Solve for the unknown and validate rate
>>> supplier_contribution = calculator.solve_value(
...     # determine with reference to settlement date
...     convention = US30U360(use_post_dates = False),
...     interest_rate = 0.050,
...     start_date = pd.Timestamp("2026-01-05", tz="UTC")
... )
>>> lender_irr = calculator.solve_rate(
...     convention = US30U360(use_post_dates = False)
... )
>>> amortisation_schedule = calculator.build_schedule(
...     profile = calculator.profile,
...     convention = US30U360(use_post_dates = False),
...     interest_rate = lender_irr
... )
>>> amortisation_schedule['value_date'] = amortisation_schedule['value_date'].dt.strftime('%Y-%m-%d')
... 
... # Step 4: Display results and schedule
>>> print(f"Supplier contribution: ${supplier_contribution:.2f}")
Supplier contribution: $61.90
>>> print(f"Lender's IRR: {lender_irr:.2%}")
Lender's IRR: 5.00%
>>> print(amortisation_schedule)
   value_date                  label   amount   capital  interest  capital_balance
0  2026-01-05                Deposit   4000.0   4000.00      0.00          4000.00
1  2026-02-05            Cost of car -10000.0 -10000.00      0.00         -6000.00
2  2026-02-05             Instalment   1000.0   1000.00      0.00         -5000.00
3  2026-02-05  Supplier contribution     61.9     61.90      0.00         -4938.10
4  2026-03-05             Instalment   1000.0    979.42    -20.58         -3958.68
5  2026-04-05             Instalment   1000.0    983.50    -16.50         -2975.18
6  2026-05-05             Instalment   1000.0    987.60    -12.40         -1987.58
7  2026-06-05             Instalment   1000.0    991.72     -8.28          -995.86
8  2026-07-05             Instalment   1000.0    995.86     -4.14            -0.00
"""
