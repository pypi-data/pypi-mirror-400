"""
Volatility Indicator Models

ATR and ATRQuantile indicators aligned with Rust backend.
"""

from typing import Literal

from pydantic import BaseModel, Field


class ATRIndicator(BaseModel):
    """Average True Range (ATR) 指标

    对应 Rust: Indicator::ATR { period }

    Returns:
        单一数值字段（不是 struct）

    Example:
        >>> atr = ATRIndicator(period=14)
        >>> atr = ATRIndicator(period=21)
    """

    type: Literal["ATR"] = "ATR"
    period: int = Field(gt=0, le=200, description="Period must be > 0 and <= 200")


class ATRQuantileIndicator(BaseModel):
    """ATR Rolling Quantile 指标

    对应 Rust: Indicator::AtrQuantile { atr_column, window, quantile }

    计算 ATR 的滚动分位数，用于动态止损等场景。

    注意：这是依赖指标，必须先定义 ATR 指标。

    Args:
        atr_column: 引用的 ATR 列名（如 "ATR|14"）
        window: 滚动窗口大小
        quantile: 分位数值 (0, 1)，0.5 表示中位数

    Returns:
        单一数值字段（不是 struct）

    Example:
        >>> atr_q = ATRQuantileIndicator(
        ...     atr_column="ATR|21",
        ...     window=40,
        ...     quantile=0.75  # 75th percentile
        ... )
    """

    type: Literal["AtrQuantile"] = "AtrQuantile"
    atr_column: str = Field(min_length=1, description="Reference to existing ATR column")
    window: int = Field(gt=0, le=500, description="Rolling window size")
    quantile: float = Field(gt=0, lt=1, description="Quantile value in (0, 1)")
