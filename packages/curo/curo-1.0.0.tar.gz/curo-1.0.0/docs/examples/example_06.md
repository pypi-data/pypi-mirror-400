# Example 6: Determine a payment in a weighted 3+n repayment profile

This example illustrates the use of ‘front loading’ a repayment profile on a proportional basis when solving for unknowns.

## Overview

This example, a variation on example 5, demonstrates how to calculate a payment schedule where the first three payments are due at the contract's start, known as 'in advance'. The remaining payments are then spread out. This structure is commonly utilised in small business loans, particularly for leasing arrangements, and variations on this exist, such as 3+33, 3+35, etc. The example leverages the `SeriesPayment` payment weighting feature, which allows for proportional distribution of an unknown payment across multiple series, rather than solving for a single value.

## Code

This example solves for an unknown instalment amount for an $10,000 advance over six months, with the first rental triple weighted, and the remaining fully weighted.

This is implemented by creating two separate `SeriesPayment` instances for each weighted instalment grouping and assigning the following values to the `weighting` attribute, as follows:

- Rental 1: `weighting = 3.0   # 3x unknown`

- Rentals 2 - 6: `weighting = 1.0  # Fully weighted` (this is the default value so is left undefined)

After the unknown values are solved we confirm the implicit interest rate (IRR) in the resulting profile equals the provided interest rate.

Notes:

- Weighting calculations require two or more `SeriesPayment` rows. Applying a weight to a single payment series does not alter the result; the entire unknown value is assigned to that series.

- Dates are optional and default to the current system date. Here, a fixed `start_date` is provided solely to ensure reproducible doctest results.

```python
import pandas as pd
from curo import (
    Calculator,
    SeriesAdvance, SeriesPayment,
    US30U360
)
 
# Step 1: Create a [Calculator](api/calculator.md) instance
calculator = Calculator()

# Step 2: Define cash flow series
calculator.add(
    SeriesAdvance(
        label="Equipment purchase",
        amount=10000.0,
    )
)
calculator.add(
    SeriesPayment(
        number_of = 1,
        label = "Rental",
        amount = None,
        weighting = 3.0   # 3x unknown
    )
)
calculator.add(
    SeriesPayment(
        number_of = 5,
        label = "Instalment",
        amount = None,
    )
)

# Step 3: Solve for the unknown and validate rate
payment_normal_weight = calculator.solve_value(
    convention = US30U360(),
    interest_rate = 0.07,
    start_date = pd.Timestamp("2026-01-05", tz="UTC")
)
lender_irr = calculator.solve_rate(
    convention = US30U360()
)
amortisation_schedule = calculator.build_schedule(
    profile = calculator.profile,
    convention = US30U360(),
    interest_rate = lender_irr
)
amortisation_schedule['post_date'] = amortisation_schedule['post_date'].dt.strftime('%Y-%m-%d')

# Step 4: Display results and schedule
print(f"Payment (normal weight): ${payment_normal_weight:.2f}") # Payment (normal weight): $1263.64
print(f"Lender IRR: {lender_irr:.2%}") # Lender IRR: 7.00%
print(amortisation_schedule)
#     post_date               label    amount   capital  interest  capital_balance
# 0  2026-01-05  Equipment purchase -10000.00 -10000.00      0.00        -10000.00
# 1  2026-01-05              Rental   3790.91   3790.91      0.00         -6209.09
# 2  2026-02-05          Instalment   1263.64   1227.41    -36.23         -4981.68
# 3  2026-03-05          Instalment   1263.64   1234.57    -29.07         -3747.11
# 4  2026-04-05          Instalment   1263.64   1241.78    -21.86         -2505.33
# 5  2026-05-05          Instalment   1263.64   1249.02    -14.62         -1256.31
# 6  2026-06-05          Instalment   1263.64   1256.31     -7.33             0.00
```

## Cash Flow Diagram

The diagram below visualizes the cash flow dynamics of a $10,000 loan over 6 months, with the first triple weighted, followed by 5 normally weighted, as implemented in the example code.

- Advance: This is shown by a blue downward arrow at the start of the timeline, indicating the value is known.

- Payments: Represented by red upward arrows, these are the regular unknown payments. Notice though how the first payment in the series coincides with the Advance and is annotated with the x3 annotation. This is the weighted payment, followed by the remaining payments regularly spaced. The timeline continues for a further month after the final payment, suggesting the contract ends at the end of the final payment period. Note however the contract end date may vary between lenders and may also depend on the number of payments taken in advance.

![Cash flow diagram for a $10,000 loan with 6 instalments, the first triple weighted](../assets/images/example-06.png)