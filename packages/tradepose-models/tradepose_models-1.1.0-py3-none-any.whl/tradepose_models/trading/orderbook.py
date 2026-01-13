"""
Orderbook Model

Provides the OrderbookEntry model for event sourcing of order lifecycle.
Each event in the order lifecycle is recorded as a separate entry.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from ..enums import OrderbookEventType
from .orders import OrderSide, OrderStatus, OrderType


class OrderbookEntry(BaseModel):
    """Orderbook event entry (Event Sourcing).

    Records each event in the order lifecycle for audit and tracking.
    Each order state change creates a new entry (immutable log).

    Event Types:
    - ORDER_CREATED (0): Order submitted to broker
    - ORDER_MODIFIED (1): Order modified (price, quantity)
    - ORDER_CANCELLED (2): Order cancelled
    - PARTIAL_FILL (3): Order partially filled
    - FULLY_FILLED (4): Order fully filled
    - REJECTED (5): Order rejected by broker
    """

    id: UUID = Field(..., description="Entry UUID (primary key)")
    user_id: UUID = Field(..., description="User UUID")
    engagement_id: UUID = Field(..., description="Engagement UUID (FK)")

    event_type: OrderbookEventType = Field(..., description="Event type (SMALLINT: 0-5)")
    raw_data: dict = Field(default_factory=dict, description="Broker raw response (JSONB)")

    # Order details
    symbol: str = Field(..., description="Trading symbol")
    side: OrderSide = Field(..., description="Order side (BUY/SELL)")
    order_type: OrderType = Field(..., description="Order type")
    quantity: Decimal = Field(..., description="Order quantity")
    filled_quantity: Decimal = Field(
        default=Decimal("0"), description="Filled quantity (for partial fills)"
    )
    price: Optional[Decimal] = Field(None, description="Order price (for limit orders)")
    filled_price: Optional[Decimal] = Field(None, description="Average filled price")

    # Broker tracking
    broker_order_id: str = Field(..., description="Broker's order ID")
    status: OrderStatus = Field(..., description="Order status")

    # Timestamps
    created_at: datetime = Field(..., description="Event timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @property
    def is_filled(self) -> bool:
        """Check if order is fully filled."""
        return self.event_type == OrderbookEventType.FULLY_FILLED

    @property
    def is_partial(self) -> bool:
        """Check if order is partially filled."""
        return self.event_type == OrderbookEventType.PARTIAL_FILL

    @property
    def remaining_quantity(self) -> Decimal:
        """Calculate remaining quantity."""
        return self.quantity - self.filled_quantity
