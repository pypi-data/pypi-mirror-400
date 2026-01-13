"""
Strategy Database Entities

Provides StrategyEntity and BlueprintEntity for database operations.
These models include UUID IDs and timestamp fields for persistence.
"""

from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

import polars as pl
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from ..enums import Freq, TradeDirection, TrendType
from ..indicators import PolarsExprField
from .indicator_spec import IndicatorSpec
from .trigger import Trigger


class StrategyEntity(BaseModel):
    """Strategy database entity.

    Represents a strategy stored in the database with UUID ID and metadata.
    Does not include blueprints (they are stored separately and linked via FK).
    """

    id: UUID = Field(..., description="Strategy UUID (primary key)")
    user_id: UUID = Field(..., description="User UUID (owner)")
    name: str = Field(..., description="Strategy name")
    base_instrument: str = Field(..., description="Base trading instrument")
    base_freq: Freq = Field(..., description="Base frequency")
    note: str = Field(default="", description="Strategy notes")

    volatility_indicator: Optional[pl.Expr] = Field(
        None,
        description="Volatility field expression",
    )
    indicators: List[IndicatorSpec] = Field(
        default_factory=list, description="Indicator specifications (list)"
    )

    is_archived: bool = Field(default=False, description="Whether strategy is archived")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

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


class BlueprintEntity(BaseModel):
    """Blueprint database entity.

    Represents a blueprint stored in the database with UUID ID and metadata.
    Linked to a strategy via strategy_id FK.
    """

    id: UUID = Field(..., description="Blueprint UUID (primary key)")
    strategy_id: UUID = Field(..., description="Parent strategy UUID (FK)")
    name: str = Field(..., description="Blueprint name")
    direction: TradeDirection = Field(..., description="Trade direction")
    trend_type: TrendType = Field(..., description="Trend type")
    entry_first: bool = Field(..., description="Whether to prioritize entry")
    note: str = Field(default="", description="Blueprint notes")

    entry_triggers: List[Trigger] = Field(default_factory=list, description="Entry trigger list")
    exit_triggers: List[Trigger] = Field(default_factory=list, description="Exit trigger list")

    is_base: bool = Field(default=False, description="Whether this is the base blueprint")
    is_archived: bool = Field(default=False, description="Whether blueprint is archived")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @field_validator("direction", mode="before")
    @classmethod
    def convert_direction(cls, v: Any) -> TradeDirection:
        """Auto-convert string to TradeDirection enum"""
        if isinstance(v, str):
            return TradeDirection(v)
        return v

    @field_validator("trend_type", mode="before")
    @classmethod
    def convert_trend_type(cls, v: Any) -> TrendType:
        """Auto-convert string to TrendType enum"""
        if isinstance(v, str):
            return TrendType(v)
        return v
