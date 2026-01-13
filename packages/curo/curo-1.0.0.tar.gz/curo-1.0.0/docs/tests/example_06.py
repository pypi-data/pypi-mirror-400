# tests/example_06.py
# pylint: disable=C0301:line-too-long
"""
Example 6: Solve Unknown Rental, Loaded First Rental

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
...         label="Equipment purchase",
...         amount=10000.0,
...     )
... )
>>> calculator.add(
...     SeriesPayment(
...         number_of = 1,
...         label = "Rental",
...         amount = None,
...         weighting = 3.0   # 3x unknown
...     )
... )
>>> calculator.add(
...     SeriesPayment(
...         number_of = 5,
...         label = "Instalment",
...         amount = None,
...     )
... )
...
... # Step 3: Solve for the unknown and validate rate
>>> payment_normal_weight = calculator.solve_value(
...     convention = US30U360(),
...     interest_rate = 0.07,
...     start_date = pd.Timestamp("2026-01-05", tz="UTC")
... )
>>> lender_irr = calculator.solve_rate(
...     convention = US30U360()
... )
>>> amortisation_schedule = calculator.build_schedule(
...     profile = calculator.profile,
...     convention = US30U360(),
...     interest_rate = lender_irr
... )
>>> amortisation_schedule['post_date'] = amortisation_schedule['post_date'].dt.strftime('%Y-%m-%d')
... 
... # Step 4: Display results and schedule
>>> print(f"Payment (normal weight): ${payment_normal_weight:.2f}")
Payment (normal weight): $1263.64
>>> print(f"Lender IRR: {lender_irr:.2%}")
Lender IRR: 7.00%
>>> print(amortisation_schedule)
    post_date               label    amount   capital  interest  capital_balance
0  2026-01-05  Equipment purchase -10000.00 -10000.00      0.00        -10000.00
1  2026-01-05              Rental   3790.91   3790.91      0.00         -6209.09
2  2026-02-05          Instalment   1263.64   1227.41    -36.23         -4981.68
3  2026-03-05          Instalment   1263.64   1234.57    -29.07         -3747.11
4  2026-04-05          Instalment   1263.64   1241.78    -21.86         -2505.33
5  2026-05-05          Instalment   1263.64   1249.02    -14.62         -1256.31
6  2026-06-05          Instalment   1263.64   1256.31     -7.33             0.00
"""
