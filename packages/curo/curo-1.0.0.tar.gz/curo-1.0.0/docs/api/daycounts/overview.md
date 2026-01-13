# Day Count Conventions

The **Curo** library provides comprehensive support for the most widely used day count conventions in financial calculations, ensuring accurate interest accrual, APR compliance, and consistent results across global markets.

These conventions are fully implemented and ready to use with any [Calculator](../../api/calculator.md) instance:

- **[Actual ISDA](actual_isda.md)**  
    Uses actual days between dates, separately handling leap and non-leap year portions.

- **[Actual/360](actual_360.md)**  
    Actual days counted against a fixed 360-day year — common in money markets.

- **[Actual/365](actual_365.md)**  
    Actual days against a 365-day year (also known as Actual/365 Fixed).

- **[EU 30/360](eu_30_360.md)**  
    Assumes 30-day months and a 360-day year, following European standard practices.

- **[EU 2023/2225 APR](eu_2008_48.md)**  
    Fully compliant with EU Directive 2023/2225 for transparent APR calculations in consumer credit.

- **[UK CONC App APR](uk_conc_app.md)**  
    Implements the UK Consumer Credit (Total Charge for Credit) Regulations for APRC disclosure.

- **[US 30/360](us_30_360.md)**  
    Standard US convention assuming 30-day months and a 360-day year (NASD/Bond Basis).

- **[US 30U/360](us_30u_360.md)**  
    Variant of US 30/360 that uniformly treats the last day of February as the 30th.

- **[US Appendix J APR](us_appendix_j.md)**
    Precise implementation of Regulation Z, Appendix J for closed-end credit APR in the United States.

Whether you're modeling loans, leases, bonds, or regulatory disclosures, Curo has the right convention built in — with full transparency and doctest-verified accuracy.