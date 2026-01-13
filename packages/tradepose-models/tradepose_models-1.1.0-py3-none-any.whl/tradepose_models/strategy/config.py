"""
Strategy Configuration Model

Provides the StrategyConfig class for complete strategy configuration.
"""

from typing import Any, Dict, List, Optional, Union
from uuid import UUID

import polars as pl
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from ..enums import Freq
from ..indicators import PolarsExprField
from .blueprint import Blueprint
from .indicator_spec import IndicatorSpec


class StrategyConfig(BaseModel):
    """完整策略配置"""

    id: Optional[UUID] = Field(None, description="策略 ID（由資料庫自動填充）")
    name: str = Field(..., description="策略名稱")
    base_instrument: str = Field(..., description="基礎交易標的")
    base_instrument_id: Optional[int] = Field(
        None, description="基礎交易標的 ID（由 Gateway 自動填充）"
    )
    base_freq: Freq = Field(..., description="基礎頻率")
    note: str = Field(default="", description="備註")

    volatility_indicator: Optional[pl.Expr] = Field(
        None,
        description="波動率欄位表達式，如 pl.col('1D_ATR|14') 或 pl.col('profile').struct.field('shape')",
    )
    indicators: List[IndicatorSpec] = Field(default_factory=list, description="指標列表")

    base_blueprint: Blueprint = Field(..., description="基礎藍圖")
    advanced_blueprints: List[Blueprint] = Field(default_factory=list, description="進階藍圖列表")

    @field_validator("volatility_indicator", mode="before")
    @classmethod
    def validate_volatility_indicator(cls, v: Any) -> Optional[pl.Expr]:
        """自動轉換 volatility_indicator 為 pl.Expr

        支援：
        - None / null
        - 字串（如 "1D_ATR|14"）→ 自動轉為 pl.col("1D_ATR|14")
        - 完整 Expr JSON（如 {"Column": "..."}）
        """
        if v is None:
            return None
        return PolarsExprField.deserialize(v)

    @field_serializer("volatility_indicator")
    def serialize_volatility_indicator(self, expr: Optional[pl.Expr]) -> Optional[dict]:
        """序列化 volatility_indicator 為 dict（與服務器格式一致）"""
        if expr is None:
            return None
        return PolarsExprField.serialize(expr)

    model_config = ConfigDict(
        arbitrary_types_allowed=True  # 允許 pl.Expr 這種自定義類型
    )

    @classmethod
    def from_api(cls, api_response: Union[Dict[str, Any], str]) -> "StrategyConfig":
        """從 API 響應創建策略配置

        Args:
            api_response: API 返回的 JSON 數據（dict 或 JSON 字符串）

        Returns:
            StrategyConfig 實例，conditions 和 price_expr 自動轉為 pl.Expr

        Example:
            >>> # 從 JSON 字符串
            >>> strategy = StrategyConfig.from_api(json_str)
            >>> # 從 dict
            >>> strategy = StrategyConfig.from_api(response.json())
            >>> # 直接使用
            >>> expr = strategy.base_blueprint.entry_triggers[0].conditions[0]
            >>> print(type(expr))  # <class 'polars.expr.expr.Expr'>
        """
        if isinstance(api_response, str):
            return cls.model_validate_json(api_response)
        else:
            return cls.model_validate(api_response)

    def to_json(self, indent: int = 2) -> str:
        """序列化為 JSON 字符串

        自動將 pl.Expr 轉為 JSON 字符串格式

        Returns:
            JSON 字符串，conditions 和 price_expr 已序列化
        """
        return self.model_dump_json(indent=indent, exclude_none=True).replace("\n", "")

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典（用於發送到 API）

        Returns:
            字典，pl.Expr 已序列化為 JSON 字符串
        """
        return self.model_dump(exclude_none=True)

    def save(self, filepath: str) -> None:
        """保存到 JSON 文件"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_json())
        print(f"✅ 策略已保存到: {filepath}")

    @classmethod
    def load(cls, filepath: str) -> "StrategyConfig":
        """從 JSON 文件加載"""
        with open(filepath, "r", encoding="utf-8") as f:
            return cls.from_api(f.read())


def parse_strategy(data: Union[Dict[str, Any], str]) -> StrategyConfig:
    """解析策略配置（最簡單的方式）

    Args:
        data: API JSON 數據（dict 或 JSON 字符串）

    Returns:
        StrategyConfig 實例，可直接訪問 pl.Expr

    Example:
        >>> import requests
        >>> # 從 API
        >>> response = requests.get("http://localhost:8080/api/v1/strategies/txf_1d_sma20_30")
        >>> strategy = parse_strategy(response.json())
        >>>
        >>> # 直接訪問 Polars Expr
        >>> conditions = strategy.base_blueprint.entry_triggers[0].conditions
        >>> print(type(conditions[0]))  # <class 'polars.expr.expr.Expr'>
        >>>
        >>> # 從 JSON 字符串
        >>> strategy = parse_strategy(json_str)
    """
    return StrategyConfig.from_api(data)
