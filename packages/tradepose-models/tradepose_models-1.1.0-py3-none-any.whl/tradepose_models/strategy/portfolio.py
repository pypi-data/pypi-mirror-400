"""
Portfolio Module

Provides Portfolio class as a selection view for indexing backtest results.
"""

from decimal import Decimal
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field

from tradepose_models.enums import BrokerType

from .registry import BlueprintSelection

if TYPE_CHECKING:
    from .config import StrategyConfig
    from .registry import StrategyRegistry


class Portfolio(BaseModel):
    """
    Portfolio - 選取視圖，用於索引回測結果

    Portfolio 儲存 BlueprintSelection 引用（而非資料複製），
    需要 StrategyRegistry 來解析實際的 StrategyConfig。

    Example:
        >>> portfolio = registry.select(
        ...     name="Q1_Portfolio",
        ...     selections=[("VA_Breakout", "va_long"), ("VA_Breakout", "va_short")],
        ...     capital=100000,
        ... )
        >>> configs = portfolio.get_configs(registry)
        >>> batch = tester.submit(strategies=configs, periods=[...])
    """

    name: str = Field(..., description="Portfolio 名稱")
    selections: List[BlueprintSelection] = Field(
        default_factory=list, description="選取的 (strategy_name, blueprint_name) 列表"
    )

    # 帳戶配置
    capital: Decimal = Field(default=Decimal("0"), description="資金")
    currency: str = Field(default="USD", description="貨幣")
    account_source: Optional[str] = Field(None, description="帳戶來源")
    broker_type: Optional[BrokerType] = Field(None, description="交易平台/Broker 類型")
    instrument_mapping: Optional[Dict[str, str]] = Field(
        None, description="商品映射 (base_instrument → target_symbol)，例如 {'BTC': 'BTCUSDT'}"
    )

    def get_configs(self, registry: "StrategyRegistry") -> List["StrategyConfig"]:
        """
        取得選取的 configs（用於傳給 BatchTester）

        Args:
            registry: StrategyRegistry 實例

        Returns:
            單一 blueprint 的 StrategyConfig 列表

        Raises:
            KeyError: 如果任何選取不存在於 registry
        """
        configs = []
        for sel in self.selections:
            entry = registry.get(sel.strategy_name, sel.blueprint_name)
            if entry is None:
                raise KeyError(
                    f"Selection not found in registry: "
                    f"strategy='{sel.strategy_name}', blueprint='{sel.blueprint_name}'"
                )
            configs.append(entry.to_single_blueprint_config())
        return configs

    def add_selection(
        self,
        strategy_name: str,
        blueprint_name: str,
    ) -> "Portfolio":
        """
        新增選取（返回新實例）

        Args:
            strategy_name: 策略名稱
            blueprint_name: Blueprint 名稱

        Returns:
            新的 Portfolio 實例
        """
        selection = BlueprintSelection(strategy_name=strategy_name, blueprint_name=blueprint_name)
        if selection in self.selections:
            return self
        return self.model_copy(update={"selections": [*self.selections, selection]})

    def remove_selection(
        self,
        strategy_name: str,
        blueprint_name: str,
    ) -> "Portfolio":
        """
        移除選取（返回新實例）

        Args:
            strategy_name: 策略名稱
            blueprint_name: Blueprint 名稱

        Returns:
            新的 Portfolio 實例
        """
        selection = BlueprintSelection(strategy_name=strategy_name, blueprint_name=blueprint_name)
        if selection not in self.selections:
            return self
        return self.model_copy(
            update={"selections": [s for s in self.selections if s != selection]}
        )

    @property
    def strategy_names(self) -> List[str]:
        """取得所有策略名稱（去重）"""
        return list(set(sel.strategy_name for sel in self.selections))

    @property
    def selection_count(self) -> int:
        """選取數量"""
        return len(self.selections)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return self.model_dump(mode="json", exclude_none=True)

    def to_json(self, indent: int = 2) -> str:
        """序列化為 JSON 字串"""
        return self.model_dump_json(indent=indent, exclude_none=True)

    def save(self, filepath: str) -> None:
        """儲存至 JSON 檔案"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    @classmethod
    def load(cls, filepath: str) -> "Portfolio":
        """從 JSON 檔案載入"""
        with open(filepath, "r", encoding="utf-8") as f:
            return cls.model_validate_json(f.read())

    @classmethod
    def from_api(cls, api_response: Union[Dict[str, Any], str]) -> "Portfolio":
        """從 API 響應建立"""
        if isinstance(api_response, str):
            return cls.model_validate_json(api_response)
        return cls.model_validate(api_response)

    def __len__(self) -> int:
        """選取數量"""
        return len(self.selections)

    def __contains__(self, item: Tuple[str, str]) -> bool:
        """檢查選取是否存在"""
        selection = BlueprintSelection(strategy_name=item[0], blueprint_name=item[1])
        return selection in self.selections

    def __iter__(self):
        """迭代選取"""
        return iter(self.selections)

    def __repr__(self) -> str:
        return (
            f"Portfolio(name={self.name!r}, selections={len(self.selections)}, "
            f"capital={self.capital}, currency={self.currency!r})"
        )
