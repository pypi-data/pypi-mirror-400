"""
Strategy Base Model

Provides the StrategyBase class with shared strategy fields (without blueprints).
Used as base class for StrategyConfig and StrategyEntity.
"""

from typing import Any, List, Optional

import polars as pl
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from ..enums import Freq
from ..indicators import PolarsExprField
from .indicator_spec import IndicatorSpec


class StrategyBase(BaseModel):
    """Strategy base class with shared fields (without blueprints).

    Contains the core strategy configuration that is shared between:
    - StrategyConfig: Local/backtest model with embedded blueprints
    - StrategyEntity: Database entity with UUID and timestamps
    """

    name: str = Field(..., description="Strategy name")
    base_instrument: str = Field(..., description="Base trading instrument")
    base_freq: Freq = Field(..., description="Base frequency")
    note: str = Field(..., description="Strategy notes")

    volatility_indicator: Optional[pl.Expr] = Field(
        None,
        description="Volatility field expression, e.g. pl.col('1D_ATR|14')",
    )
    indicators: List[IndicatorSpec] = Field(
        default_factory=list, description="Indicator specifications"
    )

    @field_validator("volatility_indicator", mode="before")
    @classmethod
    def validate_volatility_indicator(cls, v: Any) -> Optional[pl.Expr]:
        """Auto-convert volatility_indicator to pl.Expr"""
        if v is None:
            return None
        return PolarsExprField.deserialize(v)

    @field_serializer("volatility_indicator")
    def serialize_volatility_indicator(self, expr: Optional[pl.Expr]) -> Optional[dict]:
        """Serialize volatility_indicator to dict"""
        if expr is None:
            return None
        return PolarsExprField.serialize(expr)

    model_config = ConfigDict(
        arbitrary_types_allowed=True  # Allow pl.Expr custom type
    )
