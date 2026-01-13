## [1.0.0] - 2026-01-09

Initial release of Curo Python, providing instalment credit calculations aligned with Curo Dart (`2.4.3`) core functionality.

### Added
- `Calculator` class for solving cash flow values and rates using Brent's method.
- Daycount conventions: `US30360`, `Actual360`, `EU200848EC`, and others.
- Series classes: `SeriesAdvance`, `SeriesPayment`, `SeriesCharge`.
- Enums: `Mode`, `Frequency`, `DayCountTimePeriod`.
- Exceptions: `UnsolvableError`, `ValidationError`.
- MkDocs documentation with `doctest`-verified examples.

### Notes
- Feedback welcome on [GitHub](https://github.com/andrewmurphy353/curo_python) for `1.0.0`.
- Targeting feature parity with Curo Dart `2.4.3`.

Install with `pip install curo==1.0.0`.