# tests/example_02.py
# pylint: disable=C0301:line-too-long
"""
Example 2: Solve Unknown Payment, Compute Borrower's APR (Annual Percentage Rate) including fee.

Add content here...

>>> import pandas as pd
>>> from curo import (
...     Calculator, Mode,
...     SeriesAdvance, SeriesPayment, SeriesCharge,
...     US30360, EU200848EC
... )
...  
... # Step 1: Create a [Calculator](api/calculator.md) instance
>>> calculator = Calculator()
... 
... # Step 2: Define cash flow series
>>> calculator.add(
...     SeriesAdvance(label = "Loan", amount = 10000.0)
... )
>>> calculator.add(
...     SeriesPayment(
...         number_of = 6,
...         label = "Instalment",
...         amount = None,
...         mode = Mode.ARREAR
...     )
... )
>>> calculator.add(
...     SeriesCharge(
...         label = "Fee",
...         amount = 50.0,
...         mode = Mode.ARREAR
...     )
... )
...
... # Step 3: Solve for the unknown and validate rate
>>> payment = calculator.solve_value(
...     convention = US30360(),
...     interest_rate = 0.0825,
...     start_date = pd.Timestamp("2026-01-05", tz="UTC")
... )
>>> apr = calculator.solve_rate(
...     convention = EU200848EC()
... )
>>> apr_proof_schedule = calculator.build_schedule(
...     profile = calculator.profile,
...     convention = EU200848EC(),
...     interest_rate = apr)
>>> apr_proof_schedule['post_date'] = apr_proof_schedule['post_date'].dt.strftime('%Y-%m-%d')
... 
... # Step 4: Display results and schedule
>>> print(f"Monthly instalment: €{payment:.2f}")
Monthly instalment: €1707.00
>>> print(f"Annual Percentage Rate: {apr:.2%}")
Annual Percentage Rate: 10.45%
>>> print(apr_proof_schedule)
    post_date       label   amount           discount_log  amount_discounted  discounted_balance
0  2026-01-05        Loan -10000.0     f = 0 = 0.00000000      -10000.000000       -10000.000000
1  2026-02-05  Instalment   1707.0  f = 1/12 = 0.08333333        1692.922981        -8307.077019
2  2026-02-05         Fee     50.0  f = 1/12 = 0.08333333          49.587668        -8257.489351
3  2026-03-05  Instalment   1707.0  f = 2/12 = 0.16666667        1678.962049        -6578.527302
4  2026-04-05  Instalment   1707.0  f = 3/12 = 0.25000000        1665.116249        -4913.411053
5  2026-05-05  Instalment   1707.0  f = 4/12 = 0.33333333        1651.384630        -3262.026423
6  2026-06-05  Instalment   1707.0  f = 5/12 = 0.41666667        1637.766251        -1624.260172
7  2026-07-05  Instalment   1707.0  f = 6/12 = 0.50000000        1624.260177            0.000005
"""
