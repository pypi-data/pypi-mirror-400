"""Computation backends: Pure Python, NumPy SIMD, CuPy GPU, Numba JIT."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


class BackendType(Enum):
    """Available backend types."""

    PYTHON = auto()  # Pure Python (portable, slow)
    NUMPY = auto()  # NumPy SIMD (vectorized)
    CUPY = auto()  # CuPy GPU (CUDA)
    NUMBA = auto()  # Numba JIT (compiled)
    DECIMAL = auto()  # Decimal (arbitrary precision)


@dataclass
class BackendCapabilities:
    """Backend capabilities."""

    vectorized: bool = False
    gpu: bool = False
    jit: bool = False
    arbitrary_precision: bool = False
    deterministic: bool = True
    simd: bool = False


class Backend(ABC):
    """Abstract interface for computation backends."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Backend name."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> BackendCapabilities:
        """Backend capabilities."""
        pass

    @abstractmethod
    def add(self, a: Any, b: Any) -> Any:
        """Addition."""
        pass

    @abstractmethod
    def add_many(self, values: Sequence) -> Any:
        """Sum of multiple values."""
        pass

    @abstractmethod
    def kahan_sum(self, values: Sequence) -> float:
        """Compensated Kahan sum."""
        pass

    def is_available(self) -> bool:
        """Check if the backend is available."""
        return True


# =============================================================================
# PURE PYTHON BACKEND
# =============================================================================


class PythonBackend(Backend):
    """Pure Python backend - most portable."""

    @property
    def name(self) -> str:
        """Backend name."""
        return "python"

    @property
    def capabilities(self) -> BackendCapabilities:
        """Backend capabilities."""
        return BackendCapabilities(deterministic=True)

    def add(self, a: Any, b: Any) -> Any:
        """Addition."""
        return a + b

    def add_many(self, values: Sequence) -> Any:
        """Sum of multiple values."""
        return sum(values)

    def kahan_sum(self, values: Sequence) -> float:
        """Kahan summation algorithm.

        Compensates rounding errors for maximum precision
        in sums of many floats.
        """
        total = 0.0
        compensation = 0.0  # Erreur accumulée

        for value in values:
            y = float(value) - compensation
            t = total + y
            compensation = (t - total) - y
            total = t

        return total

    def neumaier_sum(self, values: Sequence) -> float:
        """Neumaier algorithm (Kahan improvement).

        Better handles the case where the added value is larger
        than the current sum.
        """
        total = 0.0
        compensation = 0.0

        for value in values:
            v = float(value)
            t = total + v

            if abs(total) >= abs(v):
                compensation += (total - t) + v
            else:
                compensation += (v - t) + total

            total = t

        return total + compensation

    def pairwise_sum(self, values: Sequence) -> float:
        """Recursive pairwise sum.

        Reduces rounding error in O(log n) instead of O(n)
        for naive sum.
        """
        n = len(values)
        if n == 0:
            return 0.0
        if n == 1:
            return float(values[0])
        if n == 2:
            return float(values[0]) + float(values[1])

        mid = n // 2
        return self.pairwise_sum(values[:mid]) + self.pairwise_sum(values[mid:])


# =============================================================================
# NUMPY BACKEND (SIMD)
# =============================================================================


class NumPyBackend(Backend):
    """NumPy backend with SIMD optimizations."""

    _np: Any = None

    def __init__(self) -> None:
        self._check_available()

    def _check_available(self) -> None:
        try:
            import numpy

            self._np = numpy
        except ImportError:
            self._np = None

    @property
    def name(self) -> str:
        """Backend name."""
        return "numpy"

    @property
    def capabilities(self) -> BackendCapabilities:
        """Backend capabilities."""
        return BackendCapabilities(vectorized=True, simd=True, deterministic=True)

    def is_available(self) -> bool:
        """Check if backend is available."""
        return self._np is not None

    def add(self, a: Any, b: Any) -> Any:
        """Addition."""
        if self._np is None:
            raise RuntimeError("NumPy not available")
        return self._np.add(a, b)

    def add_many(self, values: Sequence) -> Any:
        """Sum of multiple values."""
        if self._np is None:
            raise RuntimeError("NumPy not available")
        arr = self._np.asarray(values, dtype=self._np.float64)
        return self._np.sum(arr)

    def kahan_sum(self, values: Sequence) -> float:
        """Vectorized Kahan sum.

        Note: NumPy already uses block summation
        that reduces errors, but Kahan can be better
        for very long sequences.
        """
        if self._np is None:
            raise RuntimeError("NumPy not available")

        # For small sequences, standard NumPy sum is sufficient
        arr = self._np.asarray(values, dtype=self._np.float64)

        if len(arr) < 1000:
            return float(self._np.sum(arr))

        # For large sequences, use Kahan
        total = self._np.float64(0.0)
        compensation = self._np.float64(0.0)

        # Process in blocks for cache efficiency
        block_size = 1024
        for i in range(0, len(arr), block_size):
            block = arr[i : i + block_size]
            for v in block:
                y = v - compensation
                t = total + y
                compensation = (t - total) - y
                total = t

        return float(total)

    def vectorized_add(self, a: Sequence, b: Sequence) -> Any:
        """Vectorized addition of two arrays."""
        if self._np is None:
            raise RuntimeError("NumPy not available")
        return self._np.add(
            self._np.asarray(a, dtype=self._np.float64), self._np.asarray(b, dtype=self._np.float64)
        )


# =============================================================================
# CUPY BACKEND (GPU)
# =============================================================================


class CuPyBackend(Backend):
    """CuPy backend for GPU CUDA computation."""

    _cp: Any = None
    _device_info: str | None = None

    def __init__(self) -> None:
        self._check_available()

    def _check_available(self) -> None:
        try:
            import cupy

            self._cp = cupy
            # Check if a GPU is available
            try:
                _ = self._cp.cuda.Device(0).compute_capability
                device = self._cp.cuda.Device()
                self._device_info = f"GPU: {device.id}"
            except Exception:
                # CuPy installed but no GPU available
                self._cp = None
        except (ImportError, RuntimeError):
            # CuPy not installed or CUDA not available
            self._cp = None

    @property
    def name(self) -> str:
        """Backend name."""
        return "cupy"

    @property
    def capabilities(self) -> BackendCapabilities:
        """Backend capabilities."""
        return BackendCapabilities(
            vectorized=True,
            gpu=True,
            simd=True,
            deterministic=False,  # GPU may have non-deterministic results
        )

    def is_available(self) -> bool:
        """Check if backend is available."""
        return self._cp is not None

    def add(self, a: Any, b: Any) -> Any:
        """Addition."""
        if self._cp is None:
            raise RuntimeError("CuPy not available")
        return self._cp.add(self._cp.asarray(a), self._cp.asarray(b))

    def add_many(self, values: Sequence) -> Any:
        """Sum of multiple values."""
        if self._cp is None:
            raise RuntimeError("CuPy not available")
        arr = self._cp.asarray(values, dtype=self._cp.float64)
        return float(self._cp.sum(arr))

    def kahan_sum(self, values: Sequence) -> float:
        """Kahan sum on GPU.

        Note: Standard GPU implementation already uses
        optimized parallel reduction.
        """
        if self._cp is None:
            raise RuntimeError("CuPy not available")

        # CuPy utilise une réduction parallèle efficace
        arr = self._cp.asarray(values, dtype=self._cp.float64)
        return float(self._cp.sum(arr))

    def to_gpu(self, data: Any) -> Any:
        """Transfer data to GPU."""
        if self._cp is None:
            raise RuntimeError("CuPy not available")
        return self._cp.asarray(data)

    def to_cpu(self, data: Any) -> Any:
        """Transfer data to CPU."""
        if self._cp is None:
            raise RuntimeError("CuPy not available")
        return self._cp.asnumpy(data)


# =============================================================================
# NUMBA JIT BACKEND
# =============================================================================


class NumbaBackend(Backend):
    """Numba backend with JIT compilation."""

    _numba: Any = None
    _jit_add: Callable[[float, float], float] | None = None
    _jit_kahan: Callable[[Any], float] | None = None

    def __init__(self) -> None:
        self._check_available()

    def _check_available(self) -> None:
        try:
            import numba

            self._numba = numba
            self._compile_functions()
        except ImportError:
            self._numba = None

    def _compile_functions(self) -> None:
        """Compile JIT functions."""
        if self._numba is None:
            return

        nb = self._numba

        @nb.jit(nopython=True, cache=True, fastmath=False)
        def jit_add(a: float, b: float) -> float:
            return a + b

        @nb.jit(nopython=True, cache=True, fastmath=False)
        def jit_kahan_sum(values: Any) -> float:
            total = 0.0
            compensation = 0.0

            for i in range(len(values)):
                y = values[i] - compensation
                t = total + y
                compensation = (t - total) - y
                total = t

            return total

        self._jit_add = jit_add
        self._jit_kahan = jit_kahan_sum

    @property
    def name(self) -> str:
        """Backend name."""
        return "numba"

    @property
    def capabilities(self) -> BackendCapabilities:
        """Backend capabilities."""
        return BackendCapabilities(jit=True, simd=True, deterministic=True)

    def is_available(self) -> bool:
        """Check if backend is available."""
        return self._numba is not None

    def add(self, a: Any, b: Any) -> Any:
        """Addition."""
        if self._numba is None or self._jit_add is None:
            raise RuntimeError("Numba not available")
        return self._jit_add(float(a), float(b))

    def add_many(self, values: Sequence) -> Any:
        """Sum of multiple values."""
        if self._numba is None or self._jit_kahan is None:
            raise RuntimeError("Numba not available")
        import numpy as np

        arr = np.asarray(values, dtype=np.float64)
        return self._jit_kahan(arr)

    def kahan_sum(self, values: Sequence) -> float:
        """Compensated Kahan sum."""
        if self._numba is None or self._jit_kahan is None:
            raise RuntimeError("Numba not available")
        import numpy as np

        arr = np.asarray(values, dtype=np.float64)
        return float(self._jit_kahan(arr))


# =============================================================================
# DECIMAL BACKEND (précision arbitraire)
# =============================================================================


class DecimalBackend(Backend):
    """Backend Decimal pour précision arbitraire."""

    def __init__(self, precision: int = 50):
        from decimal import getcontext

        self._precision = precision
        getcontext().prec = precision

    @property
    def name(self) -> str:
        """Backend name."""
        return "decimal"

    @property
    def capabilities(self) -> BackendCapabilities:
        """Backend capabilities."""
        return BackendCapabilities(arbitrary_precision=True, deterministic=True)

    def add(self, a: Any, b: Any) -> Any:
        """Addition."""
        from decimal import Decimal

        return Decimal(str(a)) + Decimal(str(b))

    def add_many(self, values: Sequence) -> Any:
        """Sum of multiple values."""
        from decimal import Decimal

        return sum(Decimal(str(v)) for v in values)

    def kahan_sum(self, values: Sequence) -> float:
        """With Decimal, standard summation is already precise."""
        from decimal import Decimal

        return float(sum(Decimal(str(v)) for v in values))


# =============================================================================
# BACKEND REGISTRY
# =============================================================================

_BACKENDS: dict[str, type[Backend]] = {
    "python": PythonBackend,
    "numpy": NumPyBackend,
    "cupy": CuPyBackend,
    "numba": NumbaBackend,
    "decimal": DecimalBackend,
}


def get_backend(name: str = "auto", **kwargs: Any) -> Backend:
    """Get a backend by name.

    Args:
        name: Backend name or "auto" for automatic detection
        **kwargs: Arguments passed to backend constructor

    Returns:
        Backend instance

    """
    if name == "auto":
        # Priority: numba > cupy > numpy > python
        for backend_name in ["numba", "cupy", "numpy", "python"]:
            try:
                backend = _BACKENDS[backend_name](**kwargs)
                if backend.is_available():
                    return backend
            except Exception:
                continue
        return PythonBackend()

    if name not in _BACKENDS:
        raise ValueError(f"Unknown backend: {name}. Available: {list(_BACKENDS.keys())}")

    return _BACKENDS[name](**kwargs)


def list_available_backends() -> list[str]:
    """List available backends on this system."""
    available = []
    for name, backend_cls in _BACKENDS.items():
        try:
            backend = backend_cls()
            if backend.is_available():
                available.append(name)
        except Exception:
            continue
    return available


# =============================================================================
# BACKEND-AWARE OPERATIONS
# =============================================================================


class BackendDispatcher:
    """Dispatcher that automatically selects the best backend.

    Analyzes input data and chooses the optimal backend
    based on:
    - Data size
    - Data types
    - Backend availability
    - Precision requirements
    """

    def __init__(self, prefer_gpu: bool = False, require_determinism: bool = True):
        self.prefer_gpu = prefer_gpu
        self.require_determinism = require_determinism
        self._backends = {name: cls() for name, cls in _BACKENDS.items()}

    def select_backend(self, data_size: int, needs_precision: bool = False) -> Backend:
        """Select the best backend for the data."""
        # Arbitrary precision required
        if needs_precision:
            return self._backends["decimal"]

        # Small data: Python is sufficient
        if data_size < 100:
            return self._backends["python"]

        # GPU preferred and available
        if (
            self.prefer_gpu
            and self._backends["cupy"].is_available()
            and not self.require_determinism
        ):
            return self._backends["cupy"]

        # Numba si disponible
        if self._backends["numba"].is_available():
            return self._backends["numba"]

        # NumPy si disponible
        if self._backends["numpy"].is_available():
            return self._backends["numpy"]

        # Python fallback
        return self._backends["python"]

    def add(self, a: Any, b: Any, **hints: Any) -> Any:
        """Addition with automatic backend selection."""
        # Determine data size
        size = 1
        if hasattr(a, "__len__"):
            size = max(size, len(a))
        if hasattr(b, "__len__"):
            size = max(size, len(b))

        backend = self.select_backend(size, **hints)
        return backend.add(a, b)
