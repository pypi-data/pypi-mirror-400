"""Orderbook event type enum for event sourcing."""

from enum import IntEnum


class OrderbookEventType(IntEnum):
    """Orderbook event type (aligned with Rust #[repr(i16)]).

    Represents events in the order lifecycle for event sourcing.
    Stored as SMALLINT in PostgreSQL.
    """

    ORDER_CREATED = 0
    """Order created and submitted to broker."""

    ORDER_MODIFIED = 1
    """Order modified (price, quantity, etc.)."""

    ORDER_CANCELLED = 2
    """Order cancelled by user or system."""

    PARTIAL_FILL = 3
    """Order partially filled."""

    FULLY_FILLED = 4
    """Order fully filled."""

    REJECTED = 5
    """Order rejected by broker."""
