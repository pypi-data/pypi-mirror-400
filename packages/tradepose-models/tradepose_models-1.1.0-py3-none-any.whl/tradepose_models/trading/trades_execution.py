"""Trade execution record models."""

from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel

from tradepose_models.trading.orders import OrderSide


class TradeExecution(BaseModel):
    """Trade execution record (actual fill)."""

    trade_id: str
    order_id: str
    client_order_id: Optional[str]
    symbol: str
    broker_symbol: str
    side: OrderSide
    price: Decimal
    quantity: Decimal
    commission: Decimal
    commission_asset: str
    commission_type: Literal["maker", "taker", "fixed"]
    timestamp: datetime
    raw_data: Optional[dict] = None
