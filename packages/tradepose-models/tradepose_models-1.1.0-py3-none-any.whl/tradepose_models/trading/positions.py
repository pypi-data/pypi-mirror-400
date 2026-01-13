"""Position models."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PositionSide(str, Enum):
    """Position side."""

    LONG = "long"
    SHORT = "short"


class Position(BaseModel):
    """Unified position model."""

    # Core fields (required)
    symbol: str  # Unified symbol
    broker_symbol: str  # Broker-specific symbol
    side: PositionSide
    quantity: Decimal
    entry_price: Decimal  # Average cost
    current_price: Decimal
    unrealized_pnl: Decimal

    # With defaults (was required, now has sensible defaults)
    realized_pnl: Decimal = Decimal(0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Existing optional fields
    margin_used: Optional[Decimal] = None
    leverage: Optional[Decimal] = None
    raw_data: Optional[dict] = None

    # Broker-specific identifiers (optional)
    position_id: Optional[str] = None
    user_id: Optional[UUID] = None
    account_id: Optional[UUID] = None
    broker: Optional[str] = None
    opened_at: Optional[datetime] = None

    # Risk management (optional)
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None

    # MT5-specific (optional)
    swap: Optional[Decimal] = None
    magic: Optional[int] = None
    comment: Optional[str] = None


class ClosedPosition(BaseModel):
    """Closed position (historical)."""

    # Required fields
    symbol: str
    side: PositionSide
    quantity: Decimal
    entry_price: Decimal
    exit_price: Decimal
    realized_pnl: Decimal
    commission: Decimal
    opened_at: datetime
    closed_at: datetime

    # Broker-specific (optional)
    position_id: Optional[str] = None
    user_id: Optional[UUID] = None
    account_id: Optional[UUID] = None
    broker: Optional[str] = None
    broker_symbol: Optional[str] = None
    swap: Optional[Decimal] = None
