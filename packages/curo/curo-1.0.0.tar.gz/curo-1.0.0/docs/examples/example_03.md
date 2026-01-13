# Example 3: Determine a payment using a different interest frequency

This example demonstrates how to calculate a payment when interest is compounded at one frequency, separate from the payment schedule.

## Overview

This example illustrates how to determine the payment value in a repayment schedule with a separate compounding frequency, in this case monthly repayments with quarterly compounding interest. This setup is common in consumer loans. 

Important: Ensure the payment and interest capitalisation schedules end on the same date to avoid inconsistencies.

## Code

This example solves for an unknown instalment amount for a $10,000 loan over six months, the default [Frequency](../api/enums.md#curo.enums.Frequency) if not defined, with quarterly compound interest.

We demonstrate that this type of calculation requires at least two `SeriesPayment` series:

- A regular payment series, where you assign `is_interest_capitalised = False`, to specifiy no interest capitalisation

- A corresponding interest capitalisation series, where you assign `is_interest_capitalised = True`, and `amount = 0.0` to avoid unexpected results.

After the unknown values are solved we confirm the implicit interest rate (IRR) in the resulting profile equals the provided interest rate.

Notes:

- Date input is mandatory for these calculations to ensure the cash-flows of the regular payment series and interest capitalisation series align and share a common end-date.

```python
import pandas as pd
from curo import (
    Calculator, Frequency,
    SeriesAdvance, SeriesPayment,
    US30U360
)
 
# Step 1: Create a [Calculator](api/calculator.md) instance
calculator = Calculator()

# Step 2: Define cash flow series
calculator.add(
    SeriesAdvance(
        label="Loan",
        amount=10000.0,
        post_date_from = pd.Timestamp("2026-01-05", tz="UTC")
    )
)
calculator.add(  # Payment (capital-only) series
    SeriesPayment(
        number_of = 6,
        label = "Instalment",
        amount = None,
        frequency = Frequency.MONTHLY,
        post_date_from = pd.Timestamp("2026-2-05", tz="UTC"),
        is_interest_capitalised = False  # No interest
    )
)
calculator.add(  # Interest-only series
    SeriesPayment(
        number_of = 2,
        label = "Interest",
        amount = 0.0,  # Zero payment value (interest only)
        frequency = Frequency.QUARTERLY,
        post_date_from = pd.Timestamp("2026-04-05", tz="UTC"),
        is_interest_capitalised = True  # Add interest
    )
)

# Step 3: Solve for the unknown and validate rate
payment = calculator.solve_value(
    convention = US30U360(),
    interest_rate = 0.0825,
    start_date = pd.Timestamp("2026-01-05", tz="UTC")
)
irr = calculator.solve_rate(
    convention = US30U360()
)
amortisation_schedule = calculator.build_schedule(
    profile = calculator.profile,
    convention = US30U360(),
    interest_rate = irr
)
amortisation_schedule['post_date'] = amortisation_schedule['post_date'].dt.strftime('%Y-%m-%d')

# Step 4: Display results and schedule
print(f"Monthly instalment: ${payment:.2f}") # Monthly instalment: $1706.67
print(f"Implicit interest rate: {irr:.2%}")  # Implicit interest rate: 8.25%
print(amortisation_schedule)
#     post_date       label    amount   capital  interest  capital_balance
# 0  2026-01-05        Loan -10000.00 -10000.00      0.00        -10000.00
# 1  2026-02-05  Instalment   1706.67   1706.67      0.00         -8293.33
# 2  2026-03-05  Instalment   1706.67   1706.67      0.00         -6586.66
# 3  2026-04-05  Instalment   1706.67   1706.67      0.00         -4879.99
# 4  2026-04-05    Interest      0.00   -171.04   -171.04         -5051.03
# 5  2026-05-05  Instalment   1706.67   1706.67      0.00         -3344.36
# 6  2026-06-05  Instalment   1706.67   1706.67      0.00         -1637.69
# 7  2026-07-05  Instalment   1706.67   1706.67      0.00            68.98
# 8  2026-07-05    Interest      0.00    -68.98    -68.98             0.00
```

## Cash Flow Diagram

The diagram below visualizes the cash flow dynamics of a $10,000 loan with six monthly instalments and quarterly compounded interest, as implemented in the example code.

- Advance: This is shown by a blue downward arrow at the start of the timeline, indicating the value is known.

- Payments: The regular unknown payments are represented by red upward arrows. The short downward extension on every third payment arrow indicates that capitalised interest is added at those points.

Note: The quarterly interest capitalisation payments cannot be displayed as they have a zero value. However, there is one cash flow diagram notation used in these examples which has not been discussed yet, and that is the payment up arrows also extend for a short distance below the timeline. We use this to signify the payment includes capitalised interest. Note therefore in this example that the line only extends every third payment, when the repayment and interest schedules align. 

![Cash flow diagram for a $10,000 loan with 6 monthly instalments and quarterly compounding](../assets/images/example-03.png)