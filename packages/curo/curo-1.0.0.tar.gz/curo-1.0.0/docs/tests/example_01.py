# tests/example_01.py
# pylint: disable=C0301:line-too-long
"""
Example 1: Solving for an Unknown Cash Flow Value

This example demonstrates solving for an unknown instalment amount using
Mode.ARREAR.
 
>>> import pandas as pd
>>> from curo import Calculator, Mode, SeriesAdvance, SeriesPayment, US30360
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
...         amount = None,  # Set to None for unknown value
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
>>> irr = calculator.solve_rate(
...     convention = US30360()
... )
>>> amortisation_schedule = calculator.build_schedule(
...     profile = calculator.profile,
...     convention = US30360(),
...     interest_rate = irr)
>>> amortisation_schedule['post_date'] = amortisation_schedule['post_date'].dt.strftime('%Y-%m-%d')
... 
... # Step 4: Display results and schedule
>>> print(f"Monthly instalment: ${payment:.2f}")
Monthly instalment: $1707.00
>>> print(f"Implicit interest rate: {irr:.2%}")
Implicit interest rate: 8.25%
>>> print(amortisation_schedule)
    post_date       label   amount   capital  interest  capital_balance
0  2026-01-05        Loan -10000.0 -10000.00      0.00        -10000.00
1  2026-02-05  Instalment   1707.0   1638.25    -68.75         -8361.75
2  2026-03-05  Instalment   1707.0   1649.51    -57.49         -6712.24
3  2026-04-05  Instalment   1707.0   1660.85    -46.15         -5051.39
4  2026-05-05  Instalment   1707.0   1672.27    -34.73         -3379.12
5  2026-06-05  Instalment   1707.0   1683.77    -23.23         -1695.35
6  2026-07-05  Instalment   1707.0   1695.35    -11.65             0.00
"""
