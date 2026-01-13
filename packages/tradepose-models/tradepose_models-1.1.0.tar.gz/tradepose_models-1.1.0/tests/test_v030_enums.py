"""Unit tests for v0.3.0 enums.

Tests for:
- ExecutionMode (str enum)
- EngagementPhase (int enum, Rust #[repr(i16)] compatible, 8-state lifecycle)
- OrderbookEventType (int enum, Rust #[repr(i16)] compatible)
"""

import pytest
from tradepose_models.enums import (
    EngagementPhase,
    ExecutionMode,
    OrderbookEventType,
)


class TestExecutionMode:
    """Tests for ExecutionMode enum."""

    def test_values(self):
        """Test enum values match expected strings."""
        assert ExecutionMode.PRICE_PRIORITY.value == "price_priority"
        assert ExecutionMode.SIGNAL_PRIORITY.value == "signal_priority"

    def test_is_str_enum(self):
        """Test that ExecutionMode is a string enum."""
        assert isinstance(ExecutionMode.PRICE_PRIORITY, str)
        assert ExecutionMode.PRICE_PRIORITY == "price_priority"

    def test_json_serialization(self):
        """Test JSON serialization produces string value."""
        import json

        data = {"mode": ExecutionMode.PRICE_PRIORITY}
        serialized = json.dumps(data, default=str)
        assert '"price_priority"' in serialized

    def test_from_string(self):
        """Test creating enum from string value."""
        mode = ExecutionMode("price_priority")
        assert mode == ExecutionMode.PRICE_PRIORITY

        mode = ExecutionMode("signal_priority")
        assert mode == ExecutionMode.SIGNAL_PRIORITY

    def test_invalid_value_raises(self):
        """Test that invalid value raises ValueError."""
        with pytest.raises(ValueError):
            ExecutionMode("invalid_mode")


class TestEngagementPhase:
    """Tests for EngagementPhase enum (8-state lifecycle)."""

    def test_values(self):
        """Test enum values match expected integers (Rust #[repr(i16)] compatible)."""
        assert EngagementPhase.PENDING == 0
        assert EngagementPhase.ENTERING == 1
        assert EngagementPhase.HOLDING == 2
        assert EngagementPhase.EXITING == 3
        assert EngagementPhase.CLOSED == 4
        assert EngagementPhase.FAILED == 5
        assert EngagementPhase.CANCELLED == 6
        assert EngagementPhase.EXIT_FAILED == 7

    def test_is_int_enum(self):
        """Test that EngagementPhase is an integer enum."""
        assert isinstance(EngagementPhase.PENDING, int)
        assert EngagementPhase.PENDING + 1 == EngagementPhase.ENTERING

    def test_database_storage(self):
        """Test values are suitable for SMALLINT storage."""
        for phase in EngagementPhase:
            assert -32768 <= phase.value <= 32767, f"{phase} out of SMALLINT range"

    def test_from_int(self):
        """Test creating enum from integer value."""
        phase = EngagementPhase(0)
        assert phase == EngagementPhase.PENDING

        phase = EngagementPhase(2)
        assert phase == EngagementPhase.HOLDING

        phase = EngagementPhase(4)
        assert phase == EngagementPhase.CLOSED

    def test_invalid_value_raises(self):
        """Test that invalid value raises ValueError."""
        with pytest.raises(ValueError):
            EngagementPhase(99)

    def test_all_8_phases(self):
        """Test all 8 phases are defined."""
        assert len(list(EngagementPhase)) == 8


class TestOrderbookEventType:
    """Tests for OrderbookEventType enum."""

    def test_values(self):
        """Test enum values match expected integers (Rust #[repr(i16)] compatible)."""
        assert OrderbookEventType.ORDER_CREATED == 0
        assert OrderbookEventType.ORDER_MODIFIED == 1
        assert OrderbookEventType.ORDER_CANCELLED == 2
        assert OrderbookEventType.PARTIAL_FILL == 3
        assert OrderbookEventType.FULLY_FILLED == 4
        assert OrderbookEventType.REJECTED == 5

    def test_is_int_enum(self):
        """Test that OrderbookEventType is an integer enum."""
        assert isinstance(OrderbookEventType.ORDER_CREATED, int)

    def test_database_storage(self):
        """Test values are suitable for SMALLINT storage."""
        for event_type in OrderbookEventType:
            assert -32768 <= event_type.value <= 32767, f"{event_type} out of SMALLINT range"

    def test_event_type_ordering(self):
        """Test event types are ordered logically (0-5)."""
        event_types = list(OrderbookEventType)
        assert len(event_types) == 6
        for i, event_type in enumerate(event_types):
            assert event_type.value == i

    def test_from_int(self):
        """Test creating enum from integer value."""
        event_type = OrderbookEventType(4)
        assert event_type == OrderbookEventType.FULLY_FILLED

    def test_invalid_value_raises(self):
        """Test that invalid value raises ValueError."""
        with pytest.raises(ValueError):
            OrderbookEventType(99)
