# Example 4: Determine a supplier 0% finance scheme contribution, combined with a deferred settlement

This example demonstrates how to calculate an equipment supplier's contribution to the borrower's finance costs in 0% finance offers, and incorporates a settlement deferral by the third-party finance company.

## Overview

This example illustrates the combination of two financial concepts:

- **0% finance**: These products can be characterised as containing disclosed and non-disclosed cash flows.
    - The disclosed cash flows, which a borrower is aware of, are the full retail cost (advance) of the financed item and the payment cash flows which contain principal only; the sum of payment cash flows equals the item cost (advance), resulting in an effective 0% interest rate for the borrower.
    - The non-disclosed cash flows are the direct transactions between supplier and lender, usually a cash discount to offset the financing costs of the lender.

- **Deferred settlements**: This is where an equipment supplier with close ties to a finance company, allow them to defer payment for the equipment purchase to facilitate the pass on of benefits like reduced payments or interest to borrowers.

## Code

This example solves for an unknown supplier contribution to cover the finance cost of a $10,000 car purchase with six monthly capital payments. The calculation is from the lender viewpoint, and includes a one month supplier settlement deferral, so the calculation is performed using **values dates** defined by the each Series `value_date_from` date.

Notes:

- `SeriesAdvance`: The `post_date_from` date is the documented date of the contract, and `value_date_from` is the date of supplier settlement (undisclosed to borrower)

- `SeriesPayment`'s:
    - The borrower's documented payments are the deposit of $4000.00 and 6 x $1000.00 monthly payments, the sum equaling the advance amount (hence 0% finance).
    - The supplier's undisclosed contribution to cover the finance company's return on capital is the unknown to solve.

Deferred settlements require calculations to be undertaken using **value dates**, so we pass `use_post_dates = False` to the chosen Day Count Conventions, e.g. `US30U360(use_post_dates = False)`. This ensures the calculation is performed from the lender's perspective.

After determining the supplier contribution we show how to verify the lender's implicit return (IRR), again using `use_post_dates = False`, and display the result schedule from the lender's perspective i.e. in value-date order.

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
        label="Cost of car",
        amount=10000.0,
        post_date_from = pd.Timestamp("2026-01-05", tz="UTC"),
        value_date_from = pd.Timestamp("2026-02-05", tz="UTC")
    )
)
calculator.add(
    SeriesPayment(
        label = "Deposit",
        amount = 4000.0,
        post_date_from = pd.Timestamp("2026-01-05", tz="UTC"),
    )
)
calculator.add(
    SeriesPayment(
        label = "Supplier contribution",
        amount = None,
        post_date_from = pd.Timestamp("2026-2-05", tz="UTC"),
    )
)
calculator.add(
    SeriesPayment(
        number_of = 6,
        label = "Instalment",
        amount = 1000.0,
        post_date_from = pd.Timestamp("2026-02-05", tz="UTC")
    )
)

# Step 3: Solve for the unknown and validate rate
supplier_contribution = calculator.solve_value(
    # determine with reference to settlement date
    convention = US30U360(use_post_dates = False),
    interest_rate = 0.050,
    start_date = pd.Timestamp("2026-01-05", tz="UTC")
)
lender_irr = calculator.solve_rate(
    convention = US30U360(use_post_dates = False)
)
amortisation_schedule = calculator.build_schedule(
    profile = calculator.profile,
    convention = US30U360(use_post_dates = False),
    interest_rate = lender_irr
)
amortisation_schedule['value_date'] = amortisation_schedule['value_date'].dt.strftime('%Y-%m-%d')

# Step 4: Display results and schedule
print(f"Supplier contribution: ${supplier_contribution:.2f}") # Supplier contribution: $61.90
print(f"Lender's IRR: {lender_irr:.2%}")  # Lender's IRR: 5.00%
print(amortisation_schedule)
#    value_date                  label   amount   capital  interest  capital_balance
# 0  2026-01-05                Deposit   4000.0   4000.00      0.00          4000.00
# 1  2026-02-05            Cost of car -10000.0 -10000.00      0.00         -6000.00
# 2  2026-02-05             Instalment   1000.0   1000.00      0.00         -5000.00
# 3  2026-02-05  Supplier contribution     61.9     61.90      0.00         -4938.10
# 4  2026-03-05             Instalment   1000.0    979.42    -20.58         -3958.68
# 5  2026-04-05             Instalment   1000.0    983.50    -16.50         -2975.18
# 6  2026-05-05             Instalment   1000.0    987.60    -12.40         -1987.58
# 7  2026-06-05             Instalment   1000.0    991.72     -8.28          -995.86
# 8  2026-07-05             Instalment   1000.0    995.86     -4.14            -0.00
```

## Cash Flow Diagram

The diagram below visualizes the cash flow dynamics of a borrower's $10,000 interest-free loan with a deposit and six monthly instalments, showing the deferred supplier settlement and contribution to offset finance charges, as implemented in the example code.

- Advance: The full retail cost of the financed goods is shown as a blue downward arrow. Note that the blue advance arrow is positioned at the supplier settlement date (end of month 1) rather than the contract start, reflecting the lender's perspective.

- Payments:
    - The known borrower deposit is represented by the longer blue upward arrow at the start of the time-line.
    - The known borrower payments are represented by blue upward arrows.
    - The supplier discount required to offset the financing costs is shown by a green upward arrow above the borrower’s first payment at the end of month 1.

![Cash flow diagram for a $10,000 interest free loan with 6 instalments](../assets/images/example-04.png)