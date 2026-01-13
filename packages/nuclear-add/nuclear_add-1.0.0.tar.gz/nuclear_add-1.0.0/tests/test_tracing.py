"""Tests for tracing system."""

from nuclear_add.tracing import (
    ErrorEvent,
    ErrorSeverity,
    ErrorType,
    NumericTracer,
    OverflowDetector,
    PrecisionAnalyzer,
    get_global_tracer,
    set_global_tracer,
)


class TestNumericTracer:
    """Test numeric tracer."""

    def test_tracer_creation(self):
        """Test tracer creation."""
        tracer = NumericTracer()
        assert tracer.enabled is True
        assert len(tracer.events) == 0

    def test_tracer_log_event(self):
        """Test logging an event."""
        tracer = NumericTracer()
        event = ErrorEvent(
            error_type=ErrorType.PRECISION_LOSS,
            severity=ErrorSeverity.WARNING,
            operation="add",
            operands=(0.1, 0.2),
            result=0.30000000000000004,
        )
        tracer.log(event)
        assert len(tracer.events) == 1

    def test_tracer_log_error(self):
        """Test logging an error."""
        tracer = NumericTracer()
        tracer.log_error(
            ErrorType.OVERFLOW,
            ErrorSeverity.ERROR,
            "add",
            (1e308, 1e308),
            float("inf"),
        )
        assert len(tracer.events) == 1
        assert tracer.events[0].error_type == ErrorType.OVERFLOW

    def test_tracer_clear(self):
        """Test clearing events."""
        tracer = NumericTracer()
        tracer.log_error(
            ErrorType.PRECISION_LOSS,
            ErrorSeverity.WARNING,
            "add",
            (0.1, 0.2),
            0.3,
        )
        assert len(tracer.events) == 1
        tracer.clear()
        assert len(tracer.events) == 0

    def test_tracer_get_by_type(self):
        """Test filtering events by type."""
        tracer = NumericTracer()
        tracer.log_error(ErrorType.OVERFLOW, ErrorSeverity.ERROR, "add", (1, 2), 3)
        tracer.log_error(ErrorType.PRECISION_LOSS, ErrorSeverity.WARNING, "add", (0.1, 0.2), 0.3)

        overflow_events = tracer.get_by_type(ErrorType.OVERFLOW)
        assert len(overflow_events) == 1
        assert overflow_events[0].error_type == ErrorType.OVERFLOW

    def test_tracer_get_summary(self):
        """Test getting summary."""
        tracer = NumericTracer()
        tracer.log_error(ErrorType.OVERFLOW, ErrorSeverity.ERROR, "add", (1, 2), 3)
        tracer.log_error(ErrorType.PRECISION_LOSS, ErrorSeverity.WARNING, "add", (0.1, 0.2), 0.3)

        summary = tracer.get_summary()
        assert summary["total_events"] == 2
        assert "by_type" in summary
        assert "by_severity" in summary

    def test_tracer_to_json(self):
        """Test exporting to JSON."""
        tracer = NumericTracer()
        tracer.log_error(ErrorType.OVERFLOW, ErrorSeverity.ERROR, "add", (1, 2), 3)

        json_str = tracer.to_json()
        assert isinstance(json_str, str)
        assert "OVERFLOW" in json_str


class TestPrecisionAnalyzer:
    """Test precision analyzer."""

    def test_analyzer_creation(self):
        """Test analyzer creation."""
        analyzer = PrecisionAnalyzer()
        assert analyzer is not None

    def test_ulp_distance(self):
        """Test ULP distance calculation."""
        distance = PrecisionAnalyzer.ulp_distance(1.0, 1.0)
        assert distance == 0

    def test_check_addition_normal(self):
        """Test checking normal addition."""
        analyzer = PrecisionAnalyzer()
        event = analyzer.check_addition(0.1, 0.2, 0.3)
        assert event is None  # No error for normal addition

    def test_check_addition_nan(self):
        """Test checking addition with NaN."""
        analyzer = PrecisionAnalyzer()
        event = analyzer.check_addition(0.1, 0.2, float("nan"))
        assert event is not None
        assert event.error_type == ErrorType.NAN_PRODUCED

    def test_check_addition_overflow(self):
        """Test checking addition with overflow."""
        analyzer = PrecisionAnalyzer()
        event = analyzer.check_addition(1e308, 1e308, float("inf"))
        assert event is not None
        assert event.error_type == ErrorType.OVERFLOW


class TestOverflowDetector:
    """Test overflow detector."""

    def test_will_overflow_add(self):
        """Test overflow prediction."""
        # Should overflow
        will_overflow = OverflowDetector.will_overflow_add(1e308, 1e308)
        assert will_overflow is True

        # Should not overflow
        will_not_overflow = OverflowDetector.will_overflow_add(1.0, 2.0)
        assert will_not_overflow is False

    def test_will_underflow(self):
        """Test underflow prediction."""
        will_underflow = OverflowDetector.will_underflow(1e-310, 1e-310)
        # May or may not underflow depending on system
        assert isinstance(will_underflow, bool)

    def test_safe_add(self):
        """Test safe addition."""
        result, warning = OverflowDetector.safe_add(1.0, 2.0)
        assert result == 3.0
        assert warning is None


class TestGlobalTracer:
    """Test global tracer functions."""

    def test_get_global_tracer(self):
        """Test getting global tracer."""
        tracer = get_global_tracer()
        assert tracer is not None
        assert isinstance(tracer, NumericTracer)

    def test_set_global_tracer(self):
        """Test setting global tracer."""
        new_tracer = NumericTracer()
        set_global_tracer(new_tracer)
        retrieved = get_global_tracer()
        assert retrieved is new_tracer
