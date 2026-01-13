"""Order Event Models for Trading System.

Provides EntryOrderEvent and ExitOrderEvent for the trading decision pipeline.
These events are published to Redis Stream for consumption by Trader Service.
"""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from tradepose_models.trading.orders import OrderSide, OrderType


class EntryOrderEvent(BaseModel):
    """Entry order event (進場委託事件).

    Published by TradingDecisionJob when a trade entry signal is detected.
    Contains all information needed for Trader Service to execute entry order.

    Redis Stream: order:events:{user_id}:{account_id}
    """

    engagement_id: UUID = Field(..., description="Engagement UUID (FK)")
    account_id: UUID = Field(..., description="Account UUID for execution")
    symbol: str = Field(..., description="Trading symbol (mapped via instrument_mapping)")
    side: OrderSide = Field(..., description="Order side (BUY/SELL)")
    quantity: Decimal = Field(..., description="Order quantity (lots)")
    order_type: OrderType = Field(..., description="Order type (MARKET/LIMIT)")
    entry_price: Decimal = Field(..., description="Entry price (required)")
    sl_price: Optional[Decimal] = Field(None, description="Stop Loss price (optional)")
    tp_price: Optional[Decimal] = Field(None, description="Take Profit price (optional)")

    def to_redis_dict(self) -> dict:
        """Convert to Redis-compatible dict for Stream publishing."""
        return {
            "event_type": "entry",
            "engagement_id": str(self.engagement_id),
            "account_id": str(self.account_id),
            "symbol": self.symbol,
            "side": self.side.value,
            "quantity": str(self.quantity),
            "order_type": self.order_type.value,
            "entry_price": str(self.entry_price),
            "sl_price": str(self.sl_price) if self.sl_price else "",
            "tp_price": str(self.tp_price) if self.tp_price else "",
        }


class ExitOrderEvent(BaseModel):
    """Exit order event (出場委託事件).

    Published by TradingDecisionJob when a trade exit signal is detected.
    Contains information needed for Trader Service to execute exit order.

    Redis Stream: order:events:{user_id}:{account_id}
    """

    engagement_id: UUID = Field(..., description="Engagement UUID (FK)")
    account_id: UUID = Field(..., description="Account UUID for execution")
    symbol: str = Field(..., description="Trading symbol")
    side: OrderSide = Field(..., description="Order side (opposite of entry)")
    quantity: Decimal = Field(..., description="Order quantity (lots)")
    order_type: OrderType = Field(
        default=OrderType.MARKET, description="Order type (typically MARKET for exits)"
    )

    def to_redis_dict(self) -> dict:
        """Convert to Redis-compatible dict for Stream publishing."""
        return {
            "event_type": "exit",
            "engagement_id": str(self.engagement_id),
            "account_id": str(self.account_id),
            "symbol": self.symbol,
            "side": self.side.value,
            "quantity": str(self.quantity),
            "order_type": self.order_type.value,
        }
