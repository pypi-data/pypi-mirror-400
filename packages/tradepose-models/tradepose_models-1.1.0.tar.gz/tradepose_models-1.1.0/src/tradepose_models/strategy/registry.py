"""
Strategy Registry Module

Provides StrategyRegistry for managing strategies with (strategy_name, blueprint_name)
as unique keys. Low-coupling design - does not call external objects directly.
"""

from typing import TYPE_CHECKING, Dict, Iterator, List, Optional, Tuple

from pydantic import BaseModel, PrivateAttr

from .blueprint import Blueprint
from .config import StrategyConfig

if TYPE_CHECKING:
    from .portfolio import Portfolio


class BlueprintSelection(BaseModel):
    """選取鍵，代表 Registry 中的一個 entry"""

    strategy_name: str
    blueprint_name: str

    def to_tuple(self) -> Tuple[str, str]:
        """轉換為 tuple"""
        return (self.strategy_name, self.blueprint_name)

    @classmethod
    def from_tuple(cls, t: Tuple[str, str]) -> "BlueprintSelection":
        """從 tuple 建立"""
        return cls(strategy_name=t[0], blueprint_name=t[1])

    def __hash__(self) -> int:
        return hash(self.to_tuple())

    def __eq__(self, other: object) -> bool:
        if isinstance(other, BlueprintSelection):
            return self.to_tuple() == other.to_tuple()
        return False

    def __repr__(self) -> str:
        return f"BlueprintSelection({self.strategy_name!r}, {self.blueprint_name!r})"


class RegistryEntry(BaseModel):
    """Registry entry，儲存對原始 StrategyConfig 的引用"""

    strategy: StrategyConfig
    blueprint_name: str

    model_config = {"arbitrary_types_allowed": True}

    @property
    def key(self) -> BlueprintSelection:
        """取得選取鍵"""
        return BlueprintSelection(
            strategy_name=self.strategy.name, blueprint_name=self.blueprint_name
        )

    @property
    def blueprint(self) -> Blueprint:
        """取得此 entry 對應的 Blueprint"""
        if self.strategy.base_blueprint.name == self.blueprint_name:
            return self.strategy.base_blueprint
        for bp in self.strategy.advanced_blueprints:
            if bp.name == self.blueprint_name:
                return bp
        raise ValueError(
            f"Blueprint '{self.blueprint_name}' not found in strategy '{self.strategy.name}'"
        )

    def to_single_blueprint_config(self) -> StrategyConfig:
        """轉換為單一 blueprint 的 StrategyConfig"""
        return StrategyConfig(
            name=f"{self.strategy.name}__{self.blueprint_name}",
            base_instrument=self.strategy.base_instrument,
            base_freq=self.strategy.base_freq,
            note=self.strategy.note,
            volatility_indicator=self.strategy.volatility_indicator,
            indicators=self.strategy.indicators,
            base_blueprint=self.blueprint,
            advanced_blueprints=[],
        )

    def __repr__(self) -> str:
        return f"RegistryEntry({self.strategy.name!r}, {self.blueprint_name!r})"


class StrategyRegistry(BaseModel):
    """
    策略註冊表 - 低耦合設計，只負責儲存和保證唯一性

    使用 (strategy_name, blueprint_name) 作為唯一 key。
    當加入有多個 blueprints 的 StrategyConfig 時，自動拆成多個 entries。

    Example:
        >>> registry = StrategyRegistry()
        >>> strategy = StrategyConfig.load("va_breakout.json")
        >>> registry.add(strategy)  # 自動拆成多個 entries
        >>> configs = registry.get_configs()  # 取得所有 configs
        >>> # 使用者自己傳給 BatchTester
        >>> batch = tester.submit(strategies=configs, periods=[...])
    """

    _entries: Dict[Tuple[str, str], RegistryEntry] = PrivateAttr(default_factory=dict)
    _strategies: Dict[str, StrategyConfig] = PrivateAttr(default_factory=dict)

    def add(self, strategy: StrategyConfig) -> List[BlueprintSelection]:
        """
        加入策略，自動拆分所有 blueprints

        Args:
            strategy: 要加入的 StrategyConfig

        Returns:
            建立的 BlueprintSelection 列表

        Raises:
            ValueError: 如果任何 (strategy_name, blueprint_name) 已存在
        """
        all_bps = [strategy.base_blueprint] + list(strategy.advanced_blueprints)

        # 檢查重複
        for bp in all_bps:
            key = (strategy.name, bp.name)
            if key in self._entries:
                raise ValueError(
                    f"Entry already exists: strategy='{strategy.name}', blueprint='{bp.name}'"
                )

        # 儲存原始策略
        self._strategies[strategy.name] = strategy

        # 建立 entries
        created = []
        for bp in all_bps:
            key = (strategy.name, bp.name)
            self._entries[key] = RegistryEntry(strategy=strategy, blueprint_name=bp.name)
            created.append(BlueprintSelection(strategy_name=strategy.name, blueprint_name=bp.name))

        return created

    def add_or_replace(self, strategy: StrategyConfig) -> List[BlueprintSelection]:
        """加入或取代策略"""
        if strategy.name in self._strategies:
            self.remove(strategy.name)
        return self.add(strategy)

    def get(self, strategy_name: str, blueprint_name: str) -> Optional[RegistryEntry]:
        """取得特定 entry"""
        return self._entries.get((strategy_name, blueprint_name))

    def get_strategy(self, strategy_name: str) -> Optional[StrategyConfig]:
        """取得原始 StrategyConfig（包含所有 blueprints）"""
        return self._strategies.get(strategy_name)

    def get_configs(self) -> List[StrategyConfig]:
        """取得所有單一 blueprint configs（用於傳給 BatchTester）"""
        return [entry.to_single_blueprint_config() for entry in self._entries.values()]

    def remove(self, strategy_name: str) -> int:
        """
        移除策略的所有 entries

        Returns:
            移除的 entry 數量
        """
        keys = [k for k in self._entries if k[0] == strategy_name]
        for k in keys:
            del self._entries[k]
        self._strategies.pop(strategy_name, None)
        return len(keys)

    def select(
        self,
        name: str,
        selections: List[Tuple[str, str]],
        capital: float = 0,
        currency: str = "USD",
        account_source: Optional[str] = None,
        platform: Optional[str] = None,
    ) -> "Portfolio":
        """
        建立 Portfolio

        Args:
            name: Portfolio 名稱
            selections: 選取的 (strategy_name, blueprint_name) 列表
            capital: 資金
            currency: 貨幣
            account_source: 帳戶來源
            platform: 交易平台

        Returns:
            Portfolio 實例

        Raises:
            KeyError: 如果任何選取不存在
        """
        for sel in selections:
            if sel not in self._entries:
                raise KeyError(f"Selection not found: strategy='{sel[0]}', blueprint='{sel[1]}'")

        from .portfolio import Portfolio

        return Portfolio(
            name=name,
            selections=[
                BlueprintSelection(strategy_name=s[0], blueprint_name=s[1]) for s in selections
            ],
            capital=capital,
            currency=currency,
            account_source=account_source,
            platform=platform,
        )

    def keys(self) -> List[BlueprintSelection]:
        """取得所有選取鍵"""
        return [BlueprintSelection(strategy_name=k[0], blueprint_name=k[1]) for k in self._entries]

    def strategy_names(self) -> List[str]:
        """取得所有策略名稱"""
        return list(self._strategies.keys())

    def blueprint_names(self, strategy_name: str) -> List[str]:
        """取得特定策略的所有 blueprint 名稱"""
        return [k[1] for k in self._entries if k[0] == strategy_name]

    def __len__(self) -> int:
        """Entry 數量"""
        return len(self._entries)

    def __contains__(self, key: Tuple[str, str]) -> bool:
        """檢查 entry 是否存在"""
        return key in self._entries

    def __getitem__(self, key: Tuple[str, str]) -> RegistryEntry:
        """取得 entry: registry[('strategy', 'blueprint')]"""
        if key not in self._entries:
            raise KeyError(f"Entry not found: strategy='{key[0]}', blueprint='{key[1]}'")
        return self._entries[key]

    def __iter__(self) -> Iterator[RegistryEntry]:
        """迭代所有 entries"""
        return iter(self._entries.values())

    def __repr__(self) -> str:
        return f"StrategyRegistry(strategies={len(self._strategies)}, entries={len(self._entries)})"
