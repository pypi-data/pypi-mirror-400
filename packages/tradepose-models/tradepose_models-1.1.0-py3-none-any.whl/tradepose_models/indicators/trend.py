"""
Trend Indicator Models

SuperTrend, MACD, and ADX indicators aligned with Rust backend.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class SuperTrendIndicator(BaseModel):
    """SuperTrend 指标

    对应 Rust: Indicator::SuperTrend { multiplier, volatility_column, high, low, close }

    Args:
        multiplier: ATR 倍数（通常 2.0-3.0）
        volatility_column: 引用的波动率列名（如 "ATR|14"，注意是列名不是 struct 字段）
        high: 高价列名（默认 "high"）
        low: 低价列名（默认 "low"）
        close: 收盘价列名（默认 "close"）

    Returns:
        Struct { direction: i32, value: f64, trend: f64, ...}

    Example:
        >>> st = SuperTrendIndicator(
        ...     multiplier=3.0,
        ...     volatility_column="ATR|21"
        ... )
    """

    type: Literal["SuperTrend"] = "SuperTrend"
    multiplier: float = Field(gt=0, le=10, description="ATR multiplier (typically 2.0-3.0)")
    volatility_column: str = Field(
        min_length=1, description="Reference to volatility column (e.g., 'ATR|14')"
    )
    high: str = Field(default="high", pattern="^(high|open|low|close)$")
    low: str = Field(default="low", pattern="^(high|open|low|close)$")
    close: str = Field(default="close", pattern="^(high|open|low|close)$")
    fields: Optional[List[str]] = Field(
        default=None,
        description="Select specific fields: ['direction', 'supertrend', 'long', 'short']",
    )


class MACDIndicator(BaseModel):
    """Moving Average Convergence Divergence (MACD) 指标

    对应 Rust: Indicator::MACD { fast_period, slow_period, signal_period, column, fields }

    Returns:
        Struct { macd: f64, signal: f64, histogram: f64 }
    """

    type: Literal["MACD"] = "MACD"
    fast_period: int = Field(default=12, gt=0, le=100)
    slow_period: int = Field(default=26, gt=0, le=200)
    signal_period: int = Field(default=9, gt=0, le=50)
    column: str = Field(default="close", pattern="^(open|high|low|close|volume)$")
    fields: Optional[List[str]] = Field(
        default=None, description="Select specific fields: ['macd', 'signal', 'histogram']"
    )


class ADXIndicator(BaseModel):
    """Average Directional Index (ADX) 指标

    对应 Rust: Indicator::ADX { period, fields }

    Returns:
        Struct { adx: f64, plus_di: f64, minus_di: f64 }
    """

    type: Literal["ADX"] = "ADX"
    period: int = Field(default=14, gt=0, le=100)
    fields: Optional[List[str]] = Field(
        default=None, description="Select specific fields: ['adx', 'plus_di', 'minus_di']"
    )
