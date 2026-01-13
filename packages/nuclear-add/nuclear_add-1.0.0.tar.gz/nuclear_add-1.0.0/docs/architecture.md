# Nuclear Add Architecture

## Overview

Nuclear Add is designed with a modular architecture enabling maximum extensibility and maintainability.

```
┌─────────────────────────────────────────────────────────────┐
│                      User API Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   add()  │  │sum_safe()│  │gradient()│  │  types   │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Core Engine Layer                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            NuclearEngine                            │   │
│  │  ┌──────────────┐  ┌──────────────┐                │   │
│  │  │ NuclearConfig│  │ TypePromotion│                │   │
│  │  └──────────────┘  └──────────────┘                │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Backends   │  │    Types     │  │   Tracing    │
│              │  │              │  │              │
│ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │
│ │ Python   │ │  │ │ Interval │ │  │ │ Tracer   │ │
│ │ NumPy    │ │  │ │ DualNum  │ │  │ │ Analyzer │ │
│ │ CuPy     │ │  │ │ LazyExpr │ │  │ │ Detector │ │
│ │ Numba    │ │  │ │ Traced   │ │  │ └──────────┘ │
│ │ Decimal  │ │  │ │ Stochastic│ │  └──────────────┘
│ └──────────┘ │  │ └──────────┘ │
└──────────────┘  └──────────────┘
```

## Main Modules

### 1. Core (`core.py`)

**Responsibilities:**
- Engine configuration (`NuclearConfig`)
- Computation execution (`NuclearEngine`)
- Main `add()` function
- Error policy management
- Type promotion

**Main Classes:**
- `NuclearConfig` : Complete engine configuration
- `NuclearEngine` : Execution engine
- `TypePromotionRules` : Type conversion rules
- `OverflowPolicy`, `NaNPolicy`, `PrecisionMode`, `MathMode` : Configuration enums

### 2. Backends (`backends.py`)

**Responsibilities:**
- Abstraction of different computation backends
- Automatic selection of the best backend
- Specific optimizations (SIMD, GPU, JIT)

**Available Backends:**
- `PythonBackend` : Pure Python (portable, reference)
- `NumPyBackend` : NumPy with SIMD optimizations
- `CuPyBackend` : CUDA GPU computation (optional)
- `NumbaBackend` : JIT compilation (optional)
- `DecimalBackend` : Arbitrary precision

**Pattern:**
```python
Backend (ABC)
    ├── PythonBackend
    ├── NumPyBackend
    ├── CuPyBackend
    ├── NumbaBackend
    └── DecimalBackend
```

### 3. Types (`types.py`)

**Available Advanced Types:**

#### Interval
- Interval arithmetic for uncertainty propagation
- Guarantees that the true value is within the interval

#### DualNumber
- Automatic differentiation (forward mode)
- Computes value + derivative simultaneously

#### LazyExpr
- Lazy evaluation
- Computation graphs
- Symbolic differentiation

#### TracedValue
- Complete operation history
- Traceability for debugging

#### StochasticValue
- Stochastic rounding
- Eliminates systematic bias

### 4. Tracing (`tracing.py`)

**Responsibilities:**
- Recording numerical errors
- Precision analysis
- Overflow/underflow detection
- Reports and statistics

**Components:**
- `NumericTracer` : Main tracer
- `PrecisionAnalyzer` : Precision analysis
- `OverflowDetector` : Overflow detection
- `ErrorEvent`, `ErrorType`, `ErrorSeverity` : Event types

## Data Flow

### Simple Addition

```
User calls add(a, b)
    │
    ▼
NuclearEngine.add()
    │
    ├─► _handle_special_types()  (Interval, DualNumber, etc.)
    │
    ├─► _validate_inputs()       (Type checking)
    │
    ├─► _promote_types()         (Type conversion)
    │
    ├─► _check_pre_operation()   (Overflow detection)
    │
    ├─► _compute_add()           (Computation via backend)
    │
    └─► _check_post_operation()  (Result verification)
```

### With Tracing

```
Operation
    │
    ├─► PrecisionAnalyzer.check_addition()
    │   └─► Detect precision loss
    │
    ├─► OverflowDetector.will_overflow_add()
    │   └─► Predict overflow
    │
    └─► NumericTracer.log_error()
        └─► Record event
```

## Backend Selection

```
Data Input
    │
    ├─► Size < 100? ──► PythonBackend
    │
    ├─► Needs precision? ──► DecimalBackend
    │
    ├─► GPU available? ──► CuPyBackend
    │
    ├─► Numba available? ──► NumbaBackend
    │
    └─► NumPy available? ──► NumPyBackend
```

## Error Handling

```
Error Detection
    │
    ├─► Overflow ──► Policy: RAISE/INF/SATURATE/WRAP
    │
    ├─► NaN ──► Policy: RAISE/PROPAGATE/REPLACE
    │
    ├─► Precision Loss ──► Log to Tracer
    │
    └─► Type Coercion ──► Warning or Error
```

## Extensibility

The system is designed to be extensible:

1. **New backends** : Implement the `Backend` interface
2. **New types** : Add handling in `_handle_special_types()`
3. **New policies** : Add enums and logic in `NuclearConfig`
4. **New tracers** : Extend `NumericTracer` or create specialized analyzers
