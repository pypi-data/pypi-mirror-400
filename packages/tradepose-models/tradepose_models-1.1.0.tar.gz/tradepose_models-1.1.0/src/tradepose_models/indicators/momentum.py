"""
Momentum Indicator Models

RSI, CCI, and Stochastic indicators aligned with Rust backend.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class RSIIndicator(BaseModel):
    """Relative Strength Index (RSI) 指标

    对应 Rust: Indicator::RSI { period, column }

    Returns:
        单一数值字段（0-100 范围）
    """

    type: Literal["RSI"] = "RSI"
    period: int = Field(default=14, gt=0, le=100)
    column: str = Field(default="close", pattern="^(open|high|low|close|volume)$")


class CCIIndicator(BaseModel):
    """Commodity Channel Index (CCI) 指标

    对应 Rust: Indicator::CCI { period }

    Returns:
        单一数值字段
    """

    type: Literal["CCI"] = "CCI"
    period: int = Field(default=20, gt=0, le=100)


class StochasticIndicator(BaseModel):
    """Stochastic Oscillator 指标

    对应 Rust: Indicator::Stochastic { k_period, d_period, fields }

    Returns:
        Struct { k: f64, d: f64 }
    """

    type: Literal["Stochastic"] = "Stochastic"
    k_period: int = Field(default=14, gt=0, le=100, description="%K period")
    d_period: int = Field(default=3, gt=0, le=50, description="%D period (smoothing)")
    fields: Optional[List[str]] = Field(
        default=None, description="Select specific fields: ['k', 'd']"
    )
