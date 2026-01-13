# Example 1: Determine a payment in an arrears repayment profile

This example illustrates the use of one of two [Modes](../api/enums.md#curo.enums.Mode), a core concept in financial calculations, when solving for unknowns. 

## Overview

This example demonstrates how to calculate the value of a payment when it's due at the end of each repayment period, known as 'in arrears'. To switch to payments due at the beginning of each period ('in advance'), simply set `mode=Mode.ADVANCE` in the `SeriesPayment`.

## Code

This example solves for an unknown instalment amount for a $10,000 loan over six months, the default [Frequency](../api/enums.md#curo.enums.Frequency) if not defined.

After the unknown values are solved we confirm the implicit interest rate (IRR) in the resulting profile equals the provided interest rate.

Notes:

- Dates are optional and default to the current system date. Here, a fixed `start_date` is provided solely to ensure reproducible doctest results.

```python
import pandas as pd
from curo import Calculator, Mode, SeriesAdvance, SeriesPayment, US30360
 
# Step 1: Create a [Calculator](api/calculator.md) instance
calculator = Calculator()

# Step 2: Define cash flow series
calculator.add(
    SeriesAdvance(label = "Loan", amount = 10000.0)
)
calculator.add(
    SeriesPayment(
        number_of = 6,
        label = "Instalment",
        amount = None,  # Set to None for unknown value
        mode = Mode.ARREAR
    )
)

# Step 3: Solve for the unknown and validate rate
payment = calculator.solve_value(
    convention = US30360(),
    interest_rate = 0.0825,
    start_date = pd.Timestamp("2026-01-05", tz="UTC")
)
irr = calculator.solve_rate(
    convention = US30360()
)
amortisation_schedule = calculator.build_schedule(
    profile = calculator.profile,
    convention = US30360(),
    interest_rate = irr)
amortisation_schedule['post_date'] = amortisation_schedule['post_date'].dt.strftime('%Y-%m-%d')

# Step 4: Display results and schedule
print(f"Monthly instalment: ${payment:.2f}") # Monthly instalment: $1707.00
print(f"Implicit interest rate: {irr:.2%}")  # Implicit interest rate: 8.25%
print(amortisation_schedule)
#     post_date       label   amount   capital  interest  capital_balance
# 0  2026-01-05        Loan -10000.0 -10000.00      0.00        -10000.00
# 1  2026-02-05  Instalment   1707.0   1638.25    -68.75         -8361.75
# 2  2026-03-05  Instalment   1707.0   1649.51    -57.49         -6712.24
# 3  2026-04-05  Instalment   1707.0   1660.85    -46.15         -5051.39
# 4  2026-05-05  Instalment   1707.0   1672.27    -34.73         -3379.12
# 5  2026-06-05  Instalment   1707.0   1683.77    -23.23         -1695.35
# 6  2026-07-05  Instalment   1707.0   1695.35    -11.65             0.00
```

## Cash Flow Diagram

The diagram below visualizes the cash flow dynamics of a $10,000 loan with six instalment payments, as implemented in the example code.

- Advance: This is shown by a blue downward arrow at the start of the timeline, indicating the value is known.

- Payments: Represented by red upward arrows signifying they are unknown, these are the regular monthly payments. Notice how the first payment in the series occurs at the end of the first month after the Advance, and the remaining payments regularly thereafter.

![Cash flow diagram for a $10,000 loan with 6 monthly instalments](../assets/images/example-01.png)
