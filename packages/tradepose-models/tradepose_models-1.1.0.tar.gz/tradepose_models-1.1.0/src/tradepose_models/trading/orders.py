"""Order models for unified trading interface."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

# Import OrderStrategy from existing enums module
from tradepose_models.enums.order_strategy import OrderStrategy


class OrderSide(str, Enum):
    """Order side."""

    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    """Order types."""

    MARKET = "market"
    LIMIT = "limit"
    STOP_MARKET = "stop_market"
    STOP_LIMIT = "stop_limit"
    TAKE_PROFIT_MARKET = "take_profit_market"
    TAKE_PROFIT_LIMIT = "take_profit_limit"


class OrderStatus(str, Enum):
    """Order status."""

    PENDING_NEW = "pending_new"
    NEW = "new"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class TimeInForce(str, Enum):
    """Time in force."""

    GTC = "gtc"  # Good Till Cancel
    IOC = "ioc"  # Immediate or Cancel
    FOK = "fok"  # Fill or Kill


class OrderSubmitRequest(BaseModel):
    """Unified order submission request."""

    user_id: UUID
    account_id: UUID
    symbol: str = Field(..., description="Unified symbol (e.g., BTC-USDT)")
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    time_in_force: TimeInForce = TimeInForce.GTC
    client_order_id: Optional[str] = None
    reduce_only: bool = False

    # Trade/Portfolio context
    snapshot_price: Optional[Decimal] = Field(None, description="Market price at submission")
    trade_id: Optional[str] = Field(None, description="Backtest trade ID")
    portfolio_id: Optional[str] = Field(None, description="Portfolio ID")
    order_strategy: Optional[OrderStrategy] = Field(None, description="Execution strategy")

    extra_params: dict = Field(default_factory=dict)


class Order(BaseModel):
    """Unified order model."""

    order_id: str
    client_order_id: Optional[str]
    user_id: UUID
    account_id: UUID
    broker: str
    symbol: str = Field(..., description="Unified symbol")
    broker_symbol: str = Field(..., description="Broker-specific symbol")
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal]
    stop_price: Optional[Decimal]
    filled_quantity: Decimal
    remaining_quantity: Decimal
    average_fill_price: Optional[Decimal]
    status: OrderStatus
    time_in_force: TimeInForce
    created_at: datetime
    updated_at: datetime
    commission: Optional[Decimal] = None
    commission_asset: Optional[str] = None

    # Trade/Portfolio tracking
    trade_id: Optional[str] = None
    portfolio_id: Optional[str] = None
    order_strategy: Optional[OrderStrategy] = None

    raw_data: Optional[dict] = None  # Broker's raw response


class ExecutionReport(BaseModel):
    """Unified execution report (fill notification)."""

    execution_id: str
    order_id: str
    client_order_id: Optional[str]
    user_id: UUID
    account_id: UUID
    broker: str
    symbol: str
    broker_symbol: str
    side: OrderSide
    last_filled_quantity: Decimal
    last_filled_price: Optional[Decimal]
    cumulative_filled_quantity: Decimal
    remaining_quantity: Decimal
    order_status: OrderStatus
    commission: Decimal
    commission_asset: str
    transact_time: datetime
    received_at: datetime

    # Trade/Portfolio tracking
    trade_id: Optional[str] = None
    portfolio_id: Optional[str] = None
    order_strategy: Optional[OrderStrategy] = None

    raw_data: Optional[dict] = None
