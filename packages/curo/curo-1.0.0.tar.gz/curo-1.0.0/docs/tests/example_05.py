# tests/example_05.py
# pylint: disable=C0301:line-too-long
"""
Example 5: Solve Unknown Payment, Stepped Repayment Profile.

Add content here... needs date input

>>> import pandas as pd
>>> from curo import (
...     Calculator, Mode,
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
...     )
... )
>>> calculator.add(
...     SeriesPayment(
...         number_of = 4,
...         label = "Instalment",
...         amount = None,
...         mode = Mode.ARREAR,
...         weighting = 1.0   # 100% of unknown
...     )
... )
>>> calculator.add(
...     SeriesPayment(
...         number_of = 4,
...         label = "Instalment",
...         amount = None,
...         mode = Mode.ARREAR,
...         weighting = 0.6   # 60% of unknown
...     )
... )
>>> calculator.add(
...     SeriesPayment(
...         number_of = 4,
...         label = "Instalment",
...         amount = None,
...         mode = Mode.ARREAR,
...         weighting = 0.4   # 40% of unknown
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
Payment (normal weight): $1288.89
>>> print(f"Lender IRR: {lender_irr:.2%}")
Lender IRR: 7.00%
>>> print(amortisation_schedule)
     post_date       label    amount   capital  interest  capital_balance
0   2026-01-05        Loan -10000.00 -10000.00      0.00        -10000.00
1   2026-02-05  Instalment   1288.89   1230.56    -58.33         -8769.44
2   2026-03-05  Instalment   1288.89   1237.73    -51.16         -7531.71
3   2026-04-05  Instalment   1288.89   1244.95    -43.94         -6286.76
4   2026-05-05  Instalment   1288.89   1252.22    -36.67         -5034.54
5   2026-06-05  Instalment    773.34    743.97    -29.37         -4290.57
6   2026-07-05  Instalment    773.34    748.31    -25.03         -3542.26
7   2026-08-05  Instalment    773.34    752.68    -20.66         -2789.58
8   2026-09-05  Instalment    773.34    757.07    -16.27         -2032.51
9   2026-10-05  Instalment    515.56    503.70    -11.86         -1528.81
10  2026-11-05  Instalment    515.56    506.64     -8.92         -1022.17
11  2026-12-05  Instalment    515.56    509.60     -5.96          -512.57
12  2027-01-05  Instalment    515.56    512.57     -2.99            -0.00
"""
