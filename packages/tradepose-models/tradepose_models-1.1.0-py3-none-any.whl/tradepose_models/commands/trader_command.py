"""Trader command model (Issue #307).

Command model for Redis Stream messages sent to Trader.
Stream pattern: trader:commands:{user_id}:{node_seq}:{slot_idx}
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CommandType(str, Enum):
    """Types of commands that can be sent to Trader."""

    EXECUTE_ORDER = "execute_order"
    """Execute an order (entry, exit, SL, TP)."""

    CANCEL_ORDER = "cancel_order"
    """Cancel an existing order."""

    MODIFY_ORDER = "modify_order"
    """Modify an existing order (SL/TP levels)."""

    SYNC_BROKER_STATUS = "sync_broker_status"
    """Synchronize broker account status (positions, orders)."""


class TraderCommand(BaseModel):
    """Command sent to Trader via Redis Stream.

    Attributes:
        command_type: Type of command
        engagement_id: Associated engagement (optional for sync commands)
        account_id: Target account
        symbol: Trading symbol (for order commands)
        direction: Trade direction 1=Long, -1=Short (for order commands)
        quantity: Order quantity (for order commands)
        entry_price: Entry price (for execute commands)
        sl_price: Stop loss price (optional)
        tp_price: Take profit price (optional)
        broker_order_id: Broker's order ID (for cancel/modify)
        new_sl_price: New SL price (for modify)
        new_tp_price: New TP price (for modify)
        timestamp: Command timestamp
    """

    command_type: CommandType = Field(..., description="Type of command")
    engagement_id: Optional[UUID] = Field(None, description="Engagement UUID")
    account_id: UUID = Field(..., description="Target account UUID")

    # Order details (for EXECUTE_ORDER)
    symbol: Optional[str] = Field(None, description="Trading symbol")
    direction: Optional[int] = Field(None, description="Trade direction: 1=Long, -1=Short")
    quantity: Optional[Decimal] = Field(None, description="Order quantity")
    entry_price: Optional[Decimal] = Field(None, description="Entry price")
    sl_price: Optional[Decimal] = Field(None, description="Stop loss price")
    tp_price: Optional[Decimal] = Field(None, description="Take profit price")

    # Cancel/Modify details
    broker_order_id: Optional[str] = Field(None, description="Broker's order ID")
    new_sl_price: Optional[Decimal] = Field(None, description="New stop loss price")
    new_tp_price: Optional[Decimal] = Field(None, description="New take profit price")

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Command timestamp",
    )

    class Config:
        """Pydantic config."""

        json_encoders = {
            Decimal: str,
            UUID: str,
            datetime: lambda v: v.isoformat(),
        }
