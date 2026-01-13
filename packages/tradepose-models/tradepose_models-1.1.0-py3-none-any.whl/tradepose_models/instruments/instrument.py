"""Instrument (trading instrument) models."""

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field

from tradepose_models.broker.account_config import BrokerType, MarketType
from tradepose_models.enums import AccountSource


class InstrumentStatus(str, Enum):
    """Instrument trading status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    TRADING_HALT = "trading_halt"


class Instrument(BaseModel):
    """
    金融商品核心模型

    Unique Key: (symbol, source, market_type)
    """

    # === 資料庫 ID (從 DB 查詢時填入) ===
    id: int | None = Field(default=None, description="資料庫自動生成的 ID")

    # === 識別欄位 (Composite Key) ===
    symbol: str = Field(..., description="券商原生符號: BTCUSDT, EURUSD")
    source: AccountSource = Field(..., description="帳戶來源: BINANCE, FTMO, SHIOAJI")
    broker_type: BrokerType = Field(..., description="券商類型: binance, mt5, sinopac")
    market_type: MarketType = Field(..., description="市場類型: SPOT, FUTURES, SWAP")

    # === 貨幣定義 ===
    base_currency: str = Field(..., description="基礎資產: BTC, EUR")
    quote_currency: str = Field(..., description="計價貨幣: USDT, USD")

    # === 交易規格 (必要) ===
    tick_size: Decimal = Field(..., description="最小跳動點")
    lot_size: Decimal = Field(..., description="最小下單量")
    price_precision: int = Field(..., description="價格精度 (小數位數)")
    quantity_precision: int = Field(..., description="數量精度 (小數位數)")

    # === 交易規格 (可選) ===
    contract_size: Decimal = Field(default=Decimal("1"), description="合約大小 (衍生品)")
    contract_expiry: datetime | None = Field(default=None, description="到期日 (季度期貨)")
    min_notional: Decimal | None = Field(default=None, description="最小名義價值")

    # === 狀態 ===
    status: InstrumentStatus = Field(default=InstrumentStatus.ACTIVE)

    # === 擴展 ===
    metadata: dict = Field(default_factory=dict)


def get_instrument_key(instrument: Instrument) -> str:
    """
    獲取 Instrument 的唯一鍵值

    用於 OHLCV 資料庫主鍵或唯一索引。

    Args:
        instrument: Instrument 實例

    Returns:
        唯一的 key 字符串

    Examples:
        >>> inst = Instrument(
        ...     symbol="BTCUSDT",
        ...     source=AccountSource.BINANCE,
        ...     broker_type=BrokerType.BINANCE,
        ...     market_type=MarketType.SPOT,
        ...     base_currency="BTC",
        ...     quote_currency="USDT",
        ...     tick_size=Decimal("0.01"),
        ...     lot_size=Decimal("0.001"),
        ...     price_precision=2,
        ...     quantity_precision=3,
        ... )
        >>> get_instrument_key(inst)
        'BINANCE:spot:BTCUSDT'
    """
    return f"{instrument.source.value}:{instrument.market_type.value}:{instrument.symbol}"
