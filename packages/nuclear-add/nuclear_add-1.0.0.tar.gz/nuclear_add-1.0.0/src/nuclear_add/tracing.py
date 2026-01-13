"""Numerical error tracing system.

Allows tracking and analyzing precision problems,
overflows, NaN, and other numerical anomalies.
"""

from __future__ import annotations

import json
import math
import threading
import traceback
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any


class ErrorSeverity(Enum):
    """Severity level of numerical errors."""

    DEBUG = auto()  # Debug information
    INFO = auto()  # Normal information
    WARNING = auto()  # Minor precision loss
    ERROR = auto()  # Significant error (overflow, NaN)
    CRITICAL = auto()  # Critical error (unusable result)


class ErrorType(Enum):
    """Types of numerical errors."""

    PRECISION_LOSS = auto()  # Precision loss
    OVERFLOW = auto()  # Overflow
    UNDERFLOW = auto()  # Underflow
    NAN_PRODUCED = auto()  # Generated NaN
    INF_PRODUCED = auto()  # Generated infinity
    DENORMAL = auto()  # Denormal number
    CANCELLATION = auto()  # Catastrophic cancellation
    TYPE_COERCION = auto()  # Implicit type conversion
    ROUNDING = auto()  # Significant rounding error
    DIVISION_BY_ZERO = auto()  # Division by zero
    DOMAIN_ERROR = auto()  # Domain error (e.g., sqrt(-1))


@dataclass
class ErrorEvent:
    """Numerical error event.

    Contains all information necessary to
    understand and reproduce the error.
    """

    error_type: ErrorType
    severity: ErrorSeverity
    operation: str
    operands: tuple
    result: Any
    expected: Any | None = None
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    stack_trace: str = ""
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to serializable dictionary."""
        return {
            "error_type": self.error_type.name,
            "severity": self.severity.name,
            "operation": self.operation,
            "operands": str(self.operands),
            "result": str(self.result),
            "expected": str(self.expected) if self.expected else None,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "stack_trace": self.stack_trace,
            "context": self.context,
        }

    def __str__(self) -> str:
        return (
            f"[{self.severity.name}] {self.error_type.name}: "
            f"{self.operation}({', '.join(str(o) for o in self.operands)}) = {self.result}"
            f"{f' (expected: {self.expected})' if self.expected else ''}"
            f"{f' - {self.message}' if self.message else ''}"
        )


class NumericTracer:
    """Numerical error tracer.

    Records all numerical anomalies encountered
    during computations for post-mortem analysis.

    Example:
        >>> tracer = NumericTracer()
        >>> with tracer.trace():
        ...     result = some_computation()
        >>> tracer.get_summary()

    """

    def __init__(
        self,
        enabled: bool = True,
        min_severity: ErrorSeverity = ErrorSeverity.WARNING,
        capture_stack: bool = True,
        max_events: int = 10000,
    ):
        self.enabled = enabled
        self.min_severity = min_severity
        self.capture_stack = capture_stack
        self.max_events = max_events

        self._events: list[ErrorEvent] = []
        self._callbacks: list[Callable[[ErrorEvent], None]] = []
        self._lock = threading.Lock()
        self._context_stack: list[dict[str, Any]] = []

    def log(self, event: ErrorEvent) -> None:
        """Record an event."""
        if not self.enabled:
            return

        if event.severity.value < self.min_severity.value:
            return

        with self._lock:
            if len(self._events) >= self.max_events:
                self._events.pop(0)  # FIFO

            # Add current context
            if self._context_stack:
                event.context.update(self._context_stack[-1])

            # Capture stack trace if requested
            if self.capture_stack and not event.stack_trace:
                event.stack_trace = "\n".join(traceback.format_stack()[-5:-1])

            self._events.append(event)

            # Notify callbacks
            import contextlib

            for callback in self._callbacks:
                with contextlib.suppress(Exception):
                    callback(event)

    def log_error(
        self,
        error_type: ErrorType,
        severity: ErrorSeverity,
        operation: str,
        operands: tuple,
        result: Any,
        **kwargs: Any,
    ) -> None:
        """Shortcut to create and log an event."""
        event = ErrorEvent(
            error_type=error_type,
            severity=severity,
            operation=operation,
            operands=operands,
            result=result,
            **kwargs,
        )
        self.log(event)

    @contextmanager
    def trace(self, context: dict[str, Any] | None = None) -> Any:
        """Context manager to trace a code block."""
        if context:
            self._context_stack.append(context)
        try:
            yield self
        finally:
            if context:
                self._context_stack.pop()

    def add_callback(self, callback: Callable[[ErrorEvent], None]) -> None:
        """Add a callback called for each event."""
        self._callbacks.append(callback)

    def clear(self) -> None:
        """Clear all events."""
        with self._lock:
            self._events.clear()

    @property
    def events(self) -> list[ErrorEvent]:
        """Return a copy of events."""
        with self._lock:
            return self._events.copy()

    def get_by_type(self, error_type: ErrorType) -> list[ErrorEvent]:
        """Filter events by type."""
        return [e for e in self.events if e.error_type == error_type]

    def get_by_severity(self, min_severity: ErrorSeverity) -> list[ErrorEvent]:
        """Filter events by minimum severity."""
        return [e for e in self.events if e.severity.value >= min_severity.value]

    def get_summary(self) -> dict[str, Any]:
        """Generate a summary of detected errors.

        Returns:
            Dictionary with statistics and grouping by type

        """
        events = self.events

        if not events:
            return {"total_events": 0, "message": "No errors detected"}

        # Group by type
        by_type: dict[str, list[ErrorEvent]] = {}
        for event in events:
            type_name = event.error_type.name
            if type_name not in by_type:
                by_type[type_name] = []
            by_type[type_name].append(event)

        # Group by severity
        by_severity: dict[str, int] = {}
        for event in events:
            sev_name = event.severity.name
            by_severity[sev_name] = by_severity.get(sev_name, 0) + 1

        return {
            "total_events": len(events),
            "by_type": {k: len(v) for k, v in by_type.items()},
            "by_severity": by_severity,
            "first_event": str(events[0]) if events else None,
            "last_event": str(events[-1]) if events else None,
            "critical_count": sum(1 for e in events if e.severity == ErrorSeverity.CRITICAL),
        }

    def to_json(self) -> str:
        """Export events to JSON."""
        return json.dumps([e.to_dict() for e in self.events], indent=2)

    def __len__(self) -> int:
        return len(self._events)

    def __bool__(self) -> bool:
        return len(self._events) > 0


# =============================================================================
# SPECIALIZED ANALYZERS
# =============================================================================


class PrecisionAnalyzer:
    """Analyzes precision loss in computations.

    Detects:
    - Catastrophic cancellation
    - Significant rounding errors
    - Loss of significant digits
    """

    def __init__(self, tracer: NumericTracer | None = None):
        self.tracer = tracer or NumericTracer()

    @staticmethod
    def ulp_distance(a: float, b: float) -> int:
        """Compute ULP distance between two floats.

        ULP = Unit in the Last Place (smallest representable difference)
        """
        if math.isnan(a) or math.isnan(b):
            return -1
        if math.isinf(a) or math.isinf(b):
            return -1 if a != b else 0

        import struct

        def float_to_int(f: float) -> int:
            """Convert float to its integer representation."""
            packed = struct.pack("d", f)
            result = struct.unpack("q", packed)[0]
            return int(result)

        ia, ib = float_to_int(a), float_to_int(b)

        # Handle different signs
        if (ia < 0) != (ib < 0):
            return abs(ia) + abs(ib)

        return abs(ia - ib)

    def check_addition(self, a: float, b: float, result: float) -> ErrorEvent | None:
        """Check an addition for precision problems."""
        # Check NaN/Inf
        if math.isnan(result):
            return ErrorEvent(
                error_type=ErrorType.NAN_PRODUCED,
                severity=ErrorSeverity.ERROR,
                operation="add",
                operands=(a, b),
                result=result,
                message="NaN produced by addition",
            )

        if math.isinf(result) and not (math.isinf(a) or math.isinf(b)):
            return ErrorEvent(
                error_type=ErrorType.OVERFLOW,
                severity=ErrorSeverity.ERROR,
                operation="add",
                operands=(a, b),
                result=result,
                message="Overflow in addition",
            )

        # Check catastrophic cancellation
        if a != 0 and b != 0 and result != 0:
            # If result is much smaller than operands
            max_operand = max(abs(a), abs(b))
            if abs(result) < max_operand * 1e-10 and abs(a + b) > 0:
                # Significant precision loss
                lost_digits = -math.log10(abs(result) / max_operand)
                if lost_digits > 5:
                    return ErrorEvent(
                        error_type=ErrorType.CANCELLATION,
                        severity=ErrorSeverity.WARNING,
                        operation="add",
                        operands=(a, b),
                        result=result,
                        message=f"Catastrophic cancellation: ~{lost_digits:.0f} digits lost",
                        context={"lost_digits": lost_digits},
                    )

        return None

    def analyze_sum(self, values: list[float], result: float) -> list[ErrorEvent]:
        """Analyze a sum of multiple values."""
        events = []

        # Compare with Kahan sum
        kahan_result = self._kahan_sum(values)
        ulp_diff = self.ulp_distance(result, kahan_result)

        if ulp_diff > 10:
            events.append(
                ErrorEvent(
                    error_type=ErrorType.PRECISION_LOSS,
                    severity=ErrorSeverity.WARNING if ulp_diff < 100 else ErrorSeverity.ERROR,
                    operation="sum",
                    operands=(f"[{len(values)} values]",),
                    result=result,
                    expected=kahan_result,
                    message=f"Difference of {ulp_diff} ULP with compensated sum",
                    context={"ulp_difference": ulp_diff},
                )
            )

        return events

    @staticmethod
    def _kahan_sum(values: list[float]) -> float:
        """Kahan sum for comparison."""
        total = 0.0
        c = 0.0
        for v in values:
            y = v - c
            t = total + y
            c = (t - total) - y
            total = t
        return total


class OverflowDetector:
    """Detects overflow risks before they occur."""

    # IEEE 754 double precision limits
    MAX_FLOAT = 1.7976931348623157e308
    MIN_FLOAT = 2.2250738585072014e-308

    @classmethod
    def will_overflow_add(cls, a: float, b: float) -> bool:
        """Predict if an addition will overflow."""
        if math.isinf(a) or math.isinf(b):
            return False  # Already inf, no additional overflow

        # Check if same sign
        if a > 0 and b > 0:
            return a > cls.MAX_FLOAT - b
        elif a < 0 and b < 0:
            return a < -cls.MAX_FLOAT - b

        return False

    @classmethod
    def will_underflow(cls, a: float, b: float) -> bool:
        """Predict if an operation will underflow to denormal."""
        result = a + b
        return 0 < abs(result) < cls.MIN_FLOAT

    @classmethod
    def safe_add(cls, a: float, b: float) -> tuple[float, str | None]:
        """Addition with overflow detection.

        Returns:
            (result, warning message or None)

        """
        if cls.will_overflow_add(a, b):
            return float("inf") if (a > 0) else float("-inf"), "OVERFLOW_PREDICTED"

        result = a + b

        if math.isinf(result) and not (math.isinf(a) or math.isinf(b)):
            return result, "OVERFLOW_OCCURRED"

        if cls.will_underflow(a, b):
            return result, "UNDERFLOW_DENORMAL"

        return result, None


# =============================================================================
# GLOBAL TRACER INSTANCE
# =============================================================================

_global_tracer: NumericTracer | None = None


def get_global_tracer() -> NumericTracer:
    """Get global tracer."""
    global _global_tracer
    if _global_tracer is None:
        _global_tracer = NumericTracer()
    return _global_tracer


def set_global_tracer(tracer: NumericTracer) -> None:
    """Set global tracer."""
    global _global_tracer
    _global_tracer = tracer


@contextmanager
def trace_context(**context: Any) -> Any:
    """Context manager to add context to tracing."""
    tracer = get_global_tracer()
    with tracer.trace(context):
        yield tracer
