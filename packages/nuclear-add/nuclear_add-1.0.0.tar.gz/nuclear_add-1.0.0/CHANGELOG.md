# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-07

### Added

- Main `add()` function with support for multiple precision modes
- Flexible configuration system (`NuclearConfig`)
- Execution engine (`NuclearEngine`)
- Support for multiple backends (Python, NumPy, CuPy, Numba, Decimal)
- Advanced types:
  - `Interval` : Interval arithmetic
  - `DualNumber` : Automatic differentiation
  - `LazyExpr` : Lazy evaluation and computation graphs
  - `TracedValue` : Values with complete history
  - `StochasticValue` : Stochastic rounding
- Numerical error tracing system (`NumericTracer`)
- Specialized analyzers (`PrecisionAnalyzer`, `OverflowDetector`)
- Utility functions:
  - `sum_safe()` : Safe sum with Kahan/Neumaier/Pairwise
  - `gradient()` : Automatic gradient computation
  - `add_with_error()` : Addition with error bounds
- Vectorization support
- Units support (Pint)
- Symbolic support (SymPy) as fallback
- Complete documentation in `docs/`
- Complete test suite
- CI/CD with GitHub Actions

### Configuration

- Computation modes: `STRICT`, `FAST`, `PARANOID`
- Precision modes: `AUTO`, `FLOAT64`, `DECIMAL`, `FRACTION`, `INTERVAL`
- Overflow policies: `RAISE`, `INF`, `SATURATE`, `WRAP`
- NaN policies: `RAISE`, `PROPAGATE`, `REPLACE`

### Documentation

- Complete architecture documented
- Complete API reference
- Practical guide with examples
- Diagrams and schemas
- Design decisions documented
