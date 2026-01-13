"""
Trigger Model

Provides the Trigger class for entry/exit triggers with conditions and price expressions.
"""

from typing import Any, List, Optional

import polars as pl
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from ..enums import OrderStrategy
from ..indicators import PolarsExprField


class Trigger(BaseModel):
    """進出場觸發器

    使用方式：
    - 讀取：trigger.conditions 直接得到 List[pl.Expr]
    - 寫入：可直接賦值 pl.col("close") > 100
    """

    name: str = Field(..., description="觸發器名稱")
    order_strategy: OrderStrategy = Field(..., description="訂單策略（OrderStrategy enum）")
    priority: int = Field(..., description="優先級")
    note: Optional[str] = Field(None, description="備註")

    # 直接使用 pl.Expr 類型
    conditions: List[pl.Expr] = Field(..., description="條件列表（Polars Expr）")
    price_expr: pl.Expr = Field(..., description="價格表達式（Polars Expr）")

    @field_validator("order_strategy", mode="before")
    @classmethod
    def convert_order_strategy(cls, v: Any) -> OrderStrategy:
        """自動轉換字串為 OrderStrategy enum（保持 API 兼容性）"""
        if isinstance(v, str):
            try:
                return OrderStrategy(v)
            except ValueError:
                valid_values = [e.value for e in OrderStrategy]
                raise ValueError(
                    f"Invalid order_strategy: '{v}'. Valid values: {', '.join(valid_values)}"
                )
        return v

    @field_validator("conditions", mode="before")
    @classmethod
    def validate_conditions(cls, v: Any) -> List[pl.Expr]:
        """自動轉換 conditions 為 List[pl.Expr]"""
        if not v:
            return []

        result = []
        for item in v:
            result.append(PolarsExprField.deserialize(item))
        return result

    @field_validator("price_expr", mode="before")
    @classmethod
    def validate_price_expr(cls, v: Any) -> pl.Expr:
        """自動轉換 price_expr 為 pl.Expr"""
        return PolarsExprField.deserialize(v)

    @field_serializer("conditions")
    def serialize_conditions(self, conditions: List[pl.Expr]) -> List[dict]:
        """序列化 conditions 為 dict 列表（與服務器格式一致）"""
        return [PolarsExprField.serialize(expr) for expr in conditions]

    @field_serializer("price_expr")
    def serialize_price_expr(self, price_expr: pl.Expr) -> dict:
        """序列化 price_expr 為 dict（與服務器格式一致）"""
        return PolarsExprField.serialize(price_expr)

    model_config = ConfigDict(
        arbitrary_types_allowed=True  # 允許 pl.Expr 這種自定義類型
    )
