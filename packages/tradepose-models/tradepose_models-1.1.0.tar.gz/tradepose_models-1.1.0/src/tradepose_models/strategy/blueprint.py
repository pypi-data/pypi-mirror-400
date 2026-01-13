"""
Blueprint Model

Provides the Blueprint class for strategy blueprints with entry/exit triggers.
"""

from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from ..enums import TradeDirection, TrendType
from .trigger import Trigger


class Blueprint(BaseModel):
    """策略藍圖"""

    id: Optional[UUID] = Field(None, description="藍圖 ID（由資料庫自動填充）")
    name: str = Field(..., description="藍圖名稱")
    direction: TradeDirection = Field(..., description="方向")
    trend_type: TrendType = Field(..., description="趨勢類型")
    entry_first: bool = Field(..., description="是否優先進場")
    note: str = Field(default="", description="備註")

    entry_triggers: List[Trigger] = Field(..., description="進場觸發器列表")
    exit_triggers: List[Trigger] = Field(..., description="出場觸發器列表")

    @field_validator("direction", mode="before")
    @classmethod
    def convert_direction(cls, v: Any) -> TradeDirection:
        """自動轉換字串為 TradeDirection enum（保持 API 兼容性）"""
        if isinstance(v, str):
            try:
                return TradeDirection(v)
            except ValueError:
                valid_values = [e.value for e in TradeDirection]
                raise ValueError(
                    f"Invalid direction: '{v}'. Valid values: {', '.join(valid_values)}"
                )
        return v

    @field_validator("trend_type", mode="before")
    @classmethod
    def convert_trend_type(cls, v: Any) -> TrendType:
        """自動轉換字串為 TrendType enum（保持 API 兼容性）"""
        if isinstance(v, str):
            try:
                return TrendType(v)
            except ValueError:
                valid_values = [e.value for e in TrendType]
                raise ValueError(
                    f"Invalid trend_type: '{v}'. Valid values: {', '.join(valid_values)}"
                )
        return v
