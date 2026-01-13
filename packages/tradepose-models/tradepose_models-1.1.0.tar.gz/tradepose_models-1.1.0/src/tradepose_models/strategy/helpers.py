"""
Helper Functions for Strategy Configuration

Provides convenient factory functions for creating IndicatorSpec, Trigger, and Blueprint instances.
"""

from typing import Any, Dict, List, Optional, Union

import polars as pl

from ..enums import Freq, OrderStrategy, TradeDirection, TrendType
from .blueprint import Blueprint
from .indicator_spec import IndicatorSpec
from .trigger import Trigger


def create_indicator_spec(
    freq: Union[Freq, str],
    indicator: Dict[str, Any],
    instrument: Optional[str] = None,
    shift: int = 1,
) -> IndicatorSpec:
    """創建指標規範（簡化版工廠函數）

    使用 Indicator 靜態類創建 indicator dict，然後傳入此函數

    Args:
        freq: 頻率（使用 Freq enum 或字串）
        indicator: 指標配置（使用 Indicator 靜態類創建）
        instrument: 交易標的（顯示名稱，可選）
        shift: 位移（預設 1）

    Returns:
        IndicatorSpec 實例，可直接調用 .col() 獲取 Polars 表達式

    Examples:
        >>> from tradepose_models import Freq, Indicator, create_indicator_spec
        >>>
        >>> # 方式 1: 使用 Freq enum + Indicator 靜態類
        >>> sma_20 = create_indicator_spec(
        ...     freq=Freq.MIN_1,
        ...     indicator=Indicator.sma(period=20),
        ...     instrument="ES"
        ... )
        >>> print(sma_20.display_name())  # "ES_1min_SMA|20.close"
        >>>
        >>> # 方式 2: 使用字串（向後兼容）
        >>> atr_14 = create_indicator_spec(
        ...     freq="1D",
        ...     indicator=Indicator.atr(period=14),
        ...     shift=2
        ... )
        >>> print(atr_14.display_name())  # "1D_ATR|14_s2"
        >>>
        >>> # 方式 3: SuperTrend
        >>> st = create_indicator_spec(
        ...     freq=Freq.MIN_5,
        ...     indicator=Indicator.supertrend(multiplier=3.0, volatility_column="atr"),
        ...     instrument="BTC"
        ... )
        >>> print(st.display_name())  # "BTC_5min_ST|3.0x_atr"
        >>>
        >>> # 在策略中使用（最簡潔的寫法）
        >>> sma_50 = create_indicator_spec(Freq.MIN_1, Indicator.sma(50), "ES")
        >>> conditions = [
        ...     sma_20.col() > sma_50.col(),
        ...     pl.col("volume") > 1000
        ... ]
    """
    return IndicatorSpec(
        instrument=instrument,
        instrument_id=None,  # Will be populated by Gateway
        freq=freq,
        shift=shift,
        indicator=indicator,
    )


def create_trigger(
    name: str,
    conditions: List[pl.Expr],
    price_expr: pl.Expr,
    order_strategy: OrderStrategy = OrderStrategy.IMMEDIATE_ENTRY,
    priority: int = 1,
    note: Optional[str] = None,
) -> Trigger:
    """創建觸發器（用於開發時）

    Args:
        name: 觸發器名稱
        conditions: 條件列表，可直接使用 pl.col() 等
        price_expr: 價格表達式
        order_strategy: 訂單策略（可使用 OrderStrategy enum 或字串，預設 OrderStrategy.IMMEDIATE_ENTRY）
        priority: 優先級
        note: 備註

    Returns:
        Trigger 實例

    Example:
        >>> # 使用 OrderStrategy enum（推薦）
        >>> entry = create_trigger(
        ...     name="my_entry",
        ...     conditions=[
        ...         pl.col("sma_30") > pl.col("sma_50"),
        ...         pl.col("volume") > 1000
        ...     ],
        ...     price_expr=pl.col("open"),
        ...     order_strategy=OrderStrategy.IMMEDIATE_ENTRY
        ... )
        >>>
        >>> # 或使用字串（向後兼容）
        >>> entry = create_trigger(
        ...     name="my_entry",
        ...     conditions=[...],
        ...     price_expr=pl.col("open"),
        ...     order_strategy="ImmediateEntry"
        ... )
        >>>
        >>> # 序列化為 JSON
        >>> print(entry.model_dump_json())
    """
    return Trigger(
        name=name,
        conditions=conditions,
        price_expr=price_expr,
        order_strategy=order_strategy,
        priority=priority,
        note=note,
    )


def create_blueprint(
    name: str,
    direction: TradeDirection,
    entry_triggers: List[Trigger],
    exit_triggers: List[Trigger],
    trend_type: TrendType = TrendType.TREND,
    entry_first: bool = True,
    note: str = "",
) -> Blueprint:
    """創建藍圖（用於開發時）

    Example:
        >>> entry_trigger = create_trigger(
        ...     name="entry",
        ...     conditions=[pl.col("sma_30") > pl.col("sma_50")],
        ...     price_expr=pl.col("open")
        ... )
        >>>
        >>> exit_trigger = create_trigger(
        ...     name="exit",
        ...     conditions=[pl.col("sma_30") < pl.col("sma_50")],
        ...     price_expr=pl.col("open"),
        ...     order_strategy="ImmediateExit"
        ... )
        >>>
        >>> blueprint = create_blueprint(
        ...     name="my_strategy",
        ...     direction="Long",
        ...     entry_triggers=[entry_trigger],
        ...     exit_triggers=[exit_trigger]
        ... )
    """
    return Blueprint(
        name=name,
        direction=direction,
        trend_type=trend_type,
        entry_first=entry_first,
        note=note,
        entry_triggers=entry_triggers,
        exit_triggers=exit_triggers,
    )
