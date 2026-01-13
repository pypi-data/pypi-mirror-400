"""
Moving Average Indicator Models

SMA, EMA, SMMA, WMA indicators aligned with Rust backend.
"""

from typing import Literal

from pydantic import BaseModel, Field


class SMAIndicator(BaseModel):
    """Simple Moving Average (SMA) 指标

    对应 Rust: Indicator::SMA { period, column }

    Args:
        period: 计算周期（必须 > 0）
        column: 计算列名（默认 "close"）

    Example:
        >>> sma = SMAIndicator(period=20)
        >>> sma = SMAIndicator(period=50, column="high")
    """

    type: Literal["SMA"] = "SMA"
    period: int = Field(gt=0, le=500, description="Period must be > 0 and <= 500")
    column: str = Field(
        default="close", pattern="^(open|high|low|close|volume)$", description="OHLCV column name"
    )


class EMAIndicator(BaseModel):
    """Exponential Moving Average (EMA) 指标

    对应 Rust: Indicator::EMA { period, column }
    """

    type: Literal["EMA"] = "EMA"
    period: int = Field(gt=0, le=500)
    column: str = Field(default="close", pattern="^(open|high|low|close|volume)$")


class SMMAIndicator(BaseModel):
    """Smoothed Moving Average (SMMA) 指标

    对应 Rust: Indicator::SMMA { period, column }
    """

    type: Literal["SMMA"] = "SMMA"
    period: int = Field(gt=0, le=500)
    column: str = Field(default="close", pattern="^(open|high|low|close|volume)$")


class WMAIndicator(BaseModel):
    """Weighted Moving Average (WMA) 指标

    对应 Rust: Indicator::WMA { period, column }
    """

    type: Literal["WMA"] = "WMA"
    period: int = Field(gt=0, le=500)
    column: str = Field(default="close", pattern="^(open|high|low|close|volume)$")
