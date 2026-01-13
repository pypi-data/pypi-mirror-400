# Example 5: Determine a payment using a stepped weighted profile

This example illustrates solving unknown payments on a proportional basis to accelerate capital repayment using a stepped profile.

## Overview

This example demonstrates how to calculate a payment schedule where early and mid-term payments focus on reducing the principal faster. This method is often adopted in small business loans to align with asset depreciation rates, and leverages the `SeriesPayment` payment weighting feature. This feature allows for proportional distribution of an unknown payment across multiple series, rather than solving for a single value.

## Code

This example solves for an unknown instalment amount for a $10,000 loan over twelve months, with the first 4 instalments 100% weighted, the next 4 by 60%, and the last 4 by 40%.

This is implemented by creating three separate `SeriesPayment` instances for each weighted instalment grouping and assigning the following values to the `weighting` attribute, as follows:

- Instalments 1 - 4: `weighting = 1.0   # 100% of unknown`

- Instalments 5 - 8: `weighting = 0.6   # 60% of unknown`

- Instalments 9 - 12: `weighting = 0.4   # 40% of unknown`

After the unknown values are solved we confirm the implicit interest rate (IRR) in the resulting profile equals the provided interest rate.

Notes:

- Weighting calculations require two or more `SeriesPayment` rows. Applying a weight to a single payment series does not alter the result; the entire unknown value is assigned to that series.

- The solved for unknown is the **fully weighted** value, i.e. 100%. The provided schedule lists the weighted cash flows.

- Dates are optional and default to the current system date. Here, a fixed `start_date` is provided solely to ensure reproducible doctest results.

```python
import pandas as pd
from curo import (
    Calculator, Mode,
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
    )
)
calculator.add(
    SeriesPayment(
        number_of = 4,
        label = "Instalment",
        amount = None,
        mode = Mode.ARREAR,
        weighting = 1.0   # 100% of unknown
    )
)
calculator.add(
    SeriesPayment(
        number_of = 4,
        label = "Instalment",
        amount = None,
        mode = Mode.ARREAR,
        weighting = 0.6   # 60% of unknown
    )
)
calculator.add(
    SeriesPayment(
        number_of = 4,
        label = "Instalment",
        amount = None,
        mode = Mode.ARREAR,
        weighting = 0.4   # 40% of unknown
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
print(f"Payment (normal weight): ${payment_normal_weight:.2f}") # Payment (normal weight): $1288.89
print(f"Lender IRR: {lender_irr:.2%}")  # Lender IRR: 7.00%
print(amortisation_schedule)
#      post_date       label    amount   capital  interest  capital_balance
# 0   2026-01-05        Loan -10000.00 -10000.00      0.00        -10000.00
# 1   2026-02-05  Instalment   1288.89   1230.56    -58.33         -8769.44
# 2   2026-03-05  Instalment   1288.89   1237.73    -51.16         -7531.71
# 3   2026-04-05  Instalment   1288.89   1244.95    -43.94         -6286.76
# 4   2026-05-05  Instalment   1288.89   1252.22    -36.67         -5034.54
# 5   2026-06-05  Instalment    773.34    743.97    -29.37         -4290.57
# 6   2026-07-05  Instalment    773.34    748.31    -25.03         -3542.26
# 7   2026-08-05  Instalment    773.34    752.68    -20.66         -2789.58
# 8   2026-09-05  Instalment    773.34    757.07    -16.27         -2032.51
# 9   2026-10-05  Instalment    515.56    503.70    -11.86         -1528.81
# 10  2026-11-05  Instalment    515.56    506.64     -8.92         -1022.17
# 11  2026-12-05  Instalment    515.56    509.60     -5.96          -512.57
# 12  2027-01-05  Instalment    515.56    512.57     -2.99            -0.00
```

## Cash Flow Diagram

The diagram below visualizes the cash flow dynamics of a $10,000 loan over 12 months, with the first 4 payments 100% weighted, the next 4 by 60%, and the last 4 by 40%, as implemented in the example code.

- Advance: This is shown by a blue downward arrow at the start of the timeline, indicating the value is known.

- Payments: The regular unknown payments are represented by red upward arrows. As the example uses three 4 monthly payment series with assigned weightings of 1.00, 0.60, and 0.40 respectively, we’ve adjusted the height of the upward arrows to reflect the reduction in payment values over time, and have also used a light grey background to emphasise the stepped profile.

Note: To keep the diagram readable, repeated identical payments are condensed, with a concertina (zig-zag) line indicating omitted periods.

![Cash flow diagram for a $10,000 loan over 12 months with a stepped repayment profile](../assets/images/example-05.png)