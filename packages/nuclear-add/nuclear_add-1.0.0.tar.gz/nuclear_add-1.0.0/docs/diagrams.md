# Diagrams and Schemas

## System Architecture (Mermaid)

```mermaid
graph TB
    User[User] --> API[API Layer]
    API --> add[add function]
    API --> sum_safe[sum_safe function]
    API --> gradient[gradient function]
    
    add --> Engine[NuclearEngine]
    sum_safe --> Engine
    gradient --> Engine
    
    Engine --> Config[NuclearConfig]
    Engine --> Backend[Backend Selection]
    Engine --> Tracer[NumericTracer]
    
    Backend --> Python[PythonBackend]
    Backend --> NumPy[NumPyBackend]
    Backend --> CuPy[CuPyBackend]
    Backend --> Numba[NumbaBackend]
    Backend --> Decimal[DecimalBackend]
    
    Engine --> Types[Type System]
    Types --> Interval[Interval]
    Types --> DualNum[DualNumber]
    Types --> Lazy[LazyExpr]
    Types --> Traced[TracedValue]
    
    Tracer --> Analyzer[PrecisionAnalyzer]
    Tracer --> Detector[OverflowDetector]
```

## Addition Execution Flow

```mermaid
flowchart TD
    Start[add a b] --> CheckTypes{Special types?}
    CheckTypes -->|Interval| IntervalAdd[Interval Addition]
    CheckTypes -->|DualNumber| DualAdd[Dual Addition]
    CheckTypes -->|LazyExpr| LazyAdd[Lazy Addition]
    CheckTypes -->|Normal| Validate[Validate inputs]
    
    Validate --> Promote[Promote types]
    Promote --> PreCheck{Pre-op check}
    PreCheck -->|Overflow?| OverflowPolicy{Policy}
    OverflowPolicy -->|RAISE| RaiseError[OverflowError]
    OverflowPolicy -->|INF| Continue[Continue]
    PreCheck -->|OK| Compute[Compute]
    
    Compute --> Backend{Backend}
    Backend -->|Python| PythonOp[Python Operation]
    Backend -->|NumPy| NumPyOp[NumPy Operation]
    Backend -->|GPU| GPUOp[GPU Operation]
    
    PythonOp --> PostCheck[Post-op check]
    NumPyOp --> PostCheck
    GPUOp --> PostCheck
    
    PostCheck --> CheckNaN{NaN?}
    CheckNaN -->|Yes| NaNPolicy{Policy}
    NaNPolicy -->|RAISE| RaiseNaN[ArithmeticError]
    NaNPolicy -->|REPLACE| Replace[0.0]
    NaNPolicy -->|PROPAGATE| Continue
    
    CheckNaN -->|No| CheckInf{Inf?}
    CheckInf -->|Yes| InfPolicy{Policy}
    InfPolicy -->|RAISE| RaiseInf[OverflowError]
    InfPolicy -->|SATURATE| Saturate[MAX_FLOAT]
    
    CheckInf -->|No| Paranoid{PARANOID mode?}
    Paranoid -->|Yes| PrecisionCheck[Check precision]
    Paranoid -->|No| Return[Return result]
    
    PrecisionCheck --> Trace[Log to Tracer]
    Trace --> Return
    
    IntervalAdd --> Return
    DualAdd --> Return
    LazyAdd --> Return
    Replace --> Return
    Saturate --> Return
```

## Type Hierarchy

```mermaid
classDiagram
    class Number {
        <<abstract>>
    }
    
    class Interval {
        +low: float
        +high: float
        +midpoint()
        +width()
        +__add__()
        +__mul__()
    }
    
    class DualNumber {
        +real: float
        +dual: float
        +variable()
        +constant()
        +exp()
        +log()
    }
    
    class LazyExpr {
        +op: str
        +args: tuple
        +eval()
        +grad()
        +to_graph()
    }
    
    class TracedValue {
        +value: Any
        +trace: List
        +get_full_trace()
    }
    
    class StochasticValue {
        +value: float
        +precision: int
    }
    
    Number <|-- Interval
    Number <|-- DualNumber
    Number <|-- LazyExpr
    Number <|-- TracedValue
    Number <|-- StochasticValue
```

## Backend Architecture

```mermaid
classDiagram
    class Backend {
        <<abstract>>
        +name: str
        +capabilities: BackendCapabilities
        +add()
        +add_many()
        +kahan_sum()
        +is_available()
    }
    
    class PythonBackend {
        +kahan_sum()
        +neumaier_sum()
        +pairwise_sum()
    }
    
    class NumPyBackend {
        +vectorized_add()
        +kahan_sum()
    }
    
    class CuPyBackend {
        +to_gpu()
        +to_cpu()
    }
    
    class NumbaBackend {
        +_compile_functions()
    }
    
    class DecimalBackend {
        +precision: int
    }
    
    Backend <|-- PythonBackend
    Backend <|-- NumPyBackend
    Backend <|-- CuPyBackend
    Backend <|-- NumbaBackend
    Backend <|-- DecimalBackend
```

## Tracing System

```mermaid
sequenceDiagram
    participant User
    participant Engine
    participant Tracer
    participant Analyzer
    participant Detector
    
    User->>Engine: add(a, b)
    Engine->>Detector: will_overflow_add()
    Detector-->>Engine: True/False
    
    Engine->>Engine: compute_add()
    Engine->>Analyzer: check_addition()
    Analyzer-->>Engine: ErrorEvent or None
    
    Engine->>Tracer: log_error()
    Tracer->>Tracer: Store event
    
    Engine-->>User: result
    
    User->>Tracer: get_summary()
    Tracer-->>User: Summary dict
```

## Backend Selection

```mermaid
flowchart TD
    Start[get_backend name] --> Check{name == auto?}
    Check -->|No| Direct[Return specific backend]
    Check -->|Yes| Precision{Precision required?}
    
    Precision -->|Yes| Decimal[DecimalBackend]
    Precision -->|No| Size{Data size}
    
    Size -->|Small < 100| Python[PythonBackend]
    Size -->|Large| GPU{GPU available?}
    
    GPU -->|Yes| PreferGPU{Prefer GPU?}
    PreferGPU -->|Yes| CuPy[CuPyBackend]
    PreferGPU -->|No| Numba{Numba available?}
    
    GPU -->|No| Numba
    Numba -->|Yes| NumbaBackend[NumbaBackend]
    Numba -->|No| NumPy{NumPy available?}
    
    NumPy -->|Yes| NumPyBackend[NumPyBackend]
    NumPy -->|No| Python
    
    Direct --> Return[Return backend]
    Decimal --> Return
    Python --> Return
    CuPy --> Return
    NumbaBackend --> Return
    NumPyBackend --> Return
```

## Simple ASCII Schema

```
┌─────────────────────────────────────────────────────────┐
│                    USER APPLICATION                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   nuclear_add.add()   │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │   NuclearEngine       │
         │  ┌─────────────────┐  │
         │  │ NuclearConfig   │  │
         │  └─────────────────┘  │
         └───────────┬───────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
    ▼                ▼                ▼
┌─────────┐    ┌──────────┐    ┌──────────┐
│ Backend │    │  Types   │    │ Tracing  │
│         │    │          │    │          │
│ Python  │    │ Interval │    │ Tracer   │
│ NumPy   │    │ DualNum  │    │ Analyzer │
│ CuPy    │    │ LazyExpr │    │ Detector │
│ Numba   │    │ Traced   │    └──────────┘
│ Decimal │    │ Stochastic│
└─────────┘    └──────────┘
```

## Configuration States

```mermaid
stateDiagram-v2
    [*] --> STRICT: strict()
    [*] --> FAST: fast()
    [*] --> PARANOID: paranoid()
    [*] --> SCIENTIFIC: scientific()
    
    STRICT --> STRICT: All checks
    FAST --> FAST: Fewer checks
    PARANOID --> PARANOID: All checks + tracing
    SCIENTIFIC --> SCIENTIFIC: High precision
    
    STRICT: Overflow: RAISE
    STRICT: NaN: RAISE
    STRICT: Tracing: ON
    
    FAST: Overflow: INF
    FAST: NaN: PROPAGATE
    FAST: Tracing: OFF
    
    PARANOID: Overflow: RAISE
    PARANOID: NaN: RAISE
    PARANOID: Tracing: ALL
    PARANOID: Precision: INTERVAL
    
    SCIENTIFIC: Precision: DECIMAL
    SCIENTIFIC: Decimal prec: 100+
    SCIENTIFIC: Kahan: ON
```

## Data Flow with Special Types

```mermaid
flowchart LR
    A[Input a, b] --> B{Type check}
    
    B -->|Interval| I[Interval Arithmetic]
    B -->|DualNumber| D[Automatic Diff]
    B -->|LazyExpr| L[Lazy Evaluation]
    B -->|TracedValue| T[Value Tracing]
    B -->|Normal| N[Normal Addition]
    
    I --> R[Result Interval]
    D --> R2[Result DualNumber]
    L --> R3[Result LazyExpr]
    T --> R4[Result TracedValue]
    N --> R5[Result Number]
    
    R --> Out[Output]
    R2 --> Out
    R3 --> Out
    R4 --> Out
    R5 --> Out
```
