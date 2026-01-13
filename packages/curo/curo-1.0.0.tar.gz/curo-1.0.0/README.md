# Curo Python

![Build Status](https://github.com/andrewmurphy353/curo_python/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/github/andrewmurphy353/curo_python/graph/badge.svg?token=R4BIC2JV0L)](https://codecov.io/github/andrewmurphy353/curo_python)
![GitHub License](https://img.shields.io/github/license/andrewmurphy353/curo_python?logo=github)

Curo Python is a powerful, open-source library for performing instalment credit financial calculations, from simple loans to complex leasing and hire purchase agreements. Built from the ground up in Python, it leverages pandas DataFrames for cash flow management and SciPy for efficient solving of unknown values or rates using Brent's method.

Explore the [documentation](https://andrewmurphy353.github.io/curo_python/), or try it in action with the [Curo Calculator](https://curocalc.app), a Flutter app showcasing similar functionality.

## Why Curo Python?

Curo Python is designed for developers and financial professionals who need robust tools for fixed-term credit calculations. It goes beyond basic financial algebra, offering features typically found in commercial software, such as:

- Solving for unknown cash flow values (e.g., instalment amounts).
- Calculating implicit interest rates (e.g., IRR or APR).
- Support for multiple day count conventions, including EU and US regulatory standards.
- Flexible handling of cash flow series for loans, leases, and investment scenarios.

Check out the [examples folder](https://github.com/andrewmurphy353/curo_python/tree/main/examples) for practical use cases and accompanying cash flow diagrams that visualise inflows and outflows.

## Getting Started

### Installation

Install Curo Python using your preferred package manager:

With **pip**:
```shell
$ pip install --user curo
```
With **uv**:
```shell
$ uv add curo
```

### Basic Usage

Curo Python makes financial calculations intuitive. Below are two examples demonstrating how to solve for an unknown cash flow value and an implicit interest rate.

**Example 1: Solving for an Unknown Cash Flow Value**

Calculate the monthly instalment for a $10,000 loan over 6 months at an 8.25% annual interest rate.

```python
from curo import Calculator, Mode, SeriesAdvance, SeriesPayment, US30360

# Step 1: Create a calculator instance
calculator = Calculator()

# Step 2: Define cash flow series
calculator.add(
    SeriesAdvance(label="Loan", amount=10000.0)
)
calculator.add(
    SeriesPayment(
        number_of=6,
        label="Instalment",
        amount=None,  # Set to None for unknown value
        mode=Mode.ARREAR
    )
)

# Step 3: Solve for the instalment amount
result = calculator.solve_value(
    convention=US30360(),
    interest_rate=0.0825
)
print(f"Monthly instalment: ${result:.2f}")  # Output: $1707.00
```

**Example 2: Solving for the Implicit Interest Rate**

Find the internal rate of return (IRR) for a €10,000 loan repaid in 6 monthly instalments of €1,707.

```python
from curo import Calculator, EU200848EC, Mode, SeriesAdvance, SeriesPayment, US30360

# Step 1: Create a calculator instance
calculator = Calculator()

# Step 2: Define cash flow series
calculator.add(
    SeriesAdvance(label="Loan", amount=10000.0)
)
calculator.add(
    SeriesPayment(
        number_of=6,
        label="Instalment",
        amount=1707.00,
        mode=Mode.ARREAR
    )
)

# Step 3: Calculate the IRR and APR
irr = calculator.solve_rate(convention=US30360())
apr = calculator.solve_rate(convention=EU200848EC())

print(f"IRR: {irr * 100:.6f}")  # Output: 8.250040%
print(f"APR: {apr * 100:.6f}")  # Output: 8.569257%
```

## Key Features

### Day Count Conventions

Day count conventions determine how time intervals between cash flows are measured. Curo Python supports a wide range of conventions to meet global financial standards:

Convention|Description
:---------|:----------
Actual ISDA | Uses actual days, accounting for leap and non-leap year portions.
Actual/360 | Counts actual days, assuming a 360-day year.
Actual/365 | Counts actual days, assuming a 365-day year.
EU 30/360 | Assumes 30-day months and a 360-day year, per EU standards.
EU 2023/2225 | Compliant with EU Directive 2023/2225 for APR calculations in consumer credit.
UK CONC App | Supports UK APRC calculations for consumer credit, secured or unsecured.
US 30/360 | Default for many US calculations, using 30-day months and a 360-day year.
US 30U/360 | Like US 30/360, but treats February days uniformly as 30 days.
US Appendix J | Implements US Regulation Z, Appendix J for APR in closed-end credit.

For XIRR-style calculations (referencing the first drawdown date), pass `use_xirr_method=True` to the convention constructor. When used with `Actual/365`, this matches Microsoft Excel’s XIRR function.

### Cash Flow Diagrams

Cash flow diagrams visually represent the timing and direction of financial transactions. For example, a €10,000 loan repaid in 6 monthly instalments would look like this:

![Cash Flow Diagram](https://github.com/andrewmurphy353/curo_python/blob/main/docs/assets/images/example-01.png)

- **Down arrows**: Money received (e.g., loan advance).
- **Up arrows**: Money paid (e.g., instalments).
- **Time line**: Represents the contract term, divided into compounding periods.

## License

Copyright © 2026, [Andrew Murphy](https://github.com/andrewmurphy353).
Released under the [MIT License](LICENSE).

## Learn More

- **Examples**: Dive into practical use cases in the [examples folder](https://github.com/andrewmurphy353/curo_python/tree/main/examples).
- **Documentation**: Refer to the code [documentation](https://andrewmurphy353.github.io/curo_python/) for detailed class and method descriptions.
- **Issues & Contributions**: Report bugs or contribute on [GitHub](https://github.com/andrewmurphy353/curo_python/issues).
