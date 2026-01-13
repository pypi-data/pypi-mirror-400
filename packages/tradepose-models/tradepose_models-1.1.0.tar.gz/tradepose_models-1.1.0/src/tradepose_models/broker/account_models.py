"""Account balance and information models."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AccountBalance(BaseModel):
    """Account balance for a specific asset."""

    asset: str = Field(..., description="Asset symbol (USD, USDT, BTC, etc.)")
    total: Decimal = Field(..., description="Total balance")
    free: Decimal = Field(..., description="Available balance")
    locked: Decimal = Field(default=Decimal("0"), description="Locked balance in orders/margin")


class AccountInfo(BaseModel):
    """Account information."""

    # Basic identification
    account_id: UUID = Field(..., description="Unique account identifier")
    broker: str = Field(..., description="Broker name (mt5, binance, okx)")
    account_type: str = Field(..., description="CASH, MARGIN, FUTURES, SPOT, demo, real")

    # Status (provide defaults for backward compatibility)
    status: str = Field(default="ACTIVE", description="ACTIVE, SUSPENDED, CLOSED")
    trading_enabled: bool = Field(default=True)

    # Financial information
    total_equity: Decimal = Field(..., description="Total account equity")
    available_balance: Decimal = Field(..., description="Available balance for trading")
    used_margin: Decimal = Field(default=Decimal("0"), description="Margin currently in use")

    # Account attributes
    leverage: int = Field(default=1, description="Account leverage")
    currency: str = Field(default="USD", description="Account base currency")
    position_count: int = Field(default=0, description="Number of open positions")

    # Timestamps
    created_at: Optional[datetime] = None

    # Extended fields for broker-specific info
    broker: Optional[str] = Field(None, description="Broker name")
    total_equity: Optional[Decimal] = Field(None, description="Total equity")
    available_balance: Optional[Decimal] = Field(None, description="Available balance")
    used_margin: Optional[Decimal] = Field(None, description="Used margin")
    position_count: Optional[int] = Field(None, description="Number of open positions")
    leverage: Optional[int] = Field(None, description="Account leverage")
    currency: Optional[str] = Field(None, description="Account currency")


class MarginInfo(BaseModel):
    """Margin information."""

    initial_margin: Decimal = Field(..., description="Initial margin requirement")
    maintenance_margin: Decimal = Field(..., description="Maintenance margin requirement")
    margin_level: Decimal = Field(..., description="Margin level (%)")
    liquidation_price: Optional[Decimal] = Field(None, description="Liquidation price")
