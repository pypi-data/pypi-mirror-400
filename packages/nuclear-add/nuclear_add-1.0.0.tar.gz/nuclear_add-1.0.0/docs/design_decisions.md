# Design Decisions

## Design Philosophy

### 1. Paranoia by Default

**Decision:** Default mode is `STRICT` with all checks enabled.

**Reason:** Better to detect silent errors than ignore them. Users can choose `FAST` if they want performance.

**Impact:**
- Slightly reduced performance (acceptable for most cases)
- Proactive detection of numerical problems
- Predictable and safe behavior

### 2. Built-in Special Types

**Decision:** Native support for `Interval`, `DualNumber`, `LazyExpr`, etc.

**Reason:** These types solve real problems (uncertainty, gradients, optimization).

**Impact:**
- Unified API for different needs
- No need for external libraries for these features
- Consistent behavior

### 3. Multiple Backends

**Decision:** Architecture with multiple backends (Python, NumPy, CuPy, Numba).

**Reason:** Different needs require different tools:
- Python: portable, reference
- NumPy: performance, SIMD
- CuPy: GPU, large data
- Numba: JIT, intensive computations
- Decimal: arbitrary precision

**Impact:**
- Maximum flexibility
- Optimal performance depending on context
- Optional dependencies (no overhead)

### 4. Optional but Enabled by Default Tracing

**Decision:** Tracing enabled by default but can be disabled.

**Reason:** Tracing helps understand problems but has a performance cost.

**Impact:**
- Easier debugging
- Acceptable performance (light tracing)
- Can be disabled for production

### 5. Automatic Vectorization

**Decision:** Vectorization enabled by default.

**Reason:** Array operations are common and benefit from vectorization.

**Impact:**
- Improved performance for arrays
- Simple API (same function for scalars and arrays)
- Intuitive broadcasting

## Technical Choices

### 1. `src/` Structure

**Decision:** Use `src/nuclear_add/` structure instead of `nuclear_add/` at root.

**Reason:** Modern Python best practice:
- Avoids import conflicts
- Clearer tests (test installed package)
- Compatible with modern tools (uv, hatchling)

### 2. Hatchling instead of setuptools

**Decision:** Use `hatchling` as build backend.

**Reason:**
- More modern and simple
- Better integration with uv
- Clearer configuration

### 3. Type Hints Everywhere

**Decision:** Complete type hints in all code.

**Reason:**
- Better documentation
- Static checking with mypy
- Better IDE experience

### 4. English Docstrings

**Decision:** All documentation in English.

**Reason:**
- Industry standard
- Accessible to international audience
- Compatible with automatic documentation tools

### 5. Tests with pytest

**Decision:** Use pytest for tests.

**Reason:**
- Industry standard
- Advanced features (fixtures, parametrization)
- Easy integration with coverage

## Trade-offs

### Performance vs Security

**Choice:** `STRICT` mode by default (security) with `FAST` option (performance).

**Justification:** For 99% of cases, performance is acceptable. For the critical 1%, `FAST` is available.

### Simplicity vs Features

**Choice:** Simple API (`add()`) with many optional features.

**Justification:** Base API remains simple, advanced features accessible via parameters or special types.

### Dependencies vs Features

**Choice:** Optional dependencies (NumPy, CuPy, etc.) with pure Python fallback.

**Justification:** Module works without external dependencies, but can use optimizations if available.

## Extensibility

### Extension Points

1. **New backends** : Implement the `Backend` interface
2. **New types** : Add handling in `_handle_special_types()`
3. **New policies** : Add enums in `core.py`
4. **New tracers** : Extend `NumericTracer`

### Example: Adding a New Backend

```python
class MyCustomBackend(Backend):
    @property
    def name(self) -> str:
        return "mybackend"
    
    @property
    def capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(...)
    
    def add(self, a, b):
        # Implementation
        pass
```

## Performance Considerations

### Implemented Optimizations

1. **Lazy loading** : Backends loaded on demand
2. **Cache** : Type conversions cached
3. **Vectorization** : Use NumPy when available
4. **JIT** : Numba support for compilation

### Points of Attention

1. **PARANOID mode** : 10-100x slower (expected)
2. **Tracing** : Light overhead, can be disabled
3. **GPU backends** : CPU↔GPU transfer overhead

## Compatibility

### Python Versions

- Support: Python 3.10+
- Reason: Use of modern features (type hints, dataclasses)

### Platforms

- Windows, Linux, macOS
- GPU backends: Require CUDA (optional)

### Dependencies

- No required dependencies (works standalone)
- Optional dependencies: NumPy, CuPy, Numba, Pint, SymPy
