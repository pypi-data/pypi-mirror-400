# TradePose Models

Shared Pydantic models, enums, and schemas for the TradePose quantitative trading platform.

## What is this?

Core data models shared across all TradePose packages (gateway, client, workers). Provides:

- **Strategy Configuration** - Complete strategy definition with blueprints and triggers
- **Registry & Portfolio** - Multi-strategy management with unique key indexing
- **Enumerations** - Type-safe enums for frequencies, directions, platforms
- **Polars Schemas** - DataFrame schemas for trades, performance, OHLCV
- **Type Safety** - Full Pydantic validation with IDE autocomplete

## Installation

```bash
pip install tradepose-models
```

**Requirements:**
- Python 3.13+
- Dependencies: pydantic, polars

---

## Quick Start

### Strategy Configuration

```python
from tradepose_models.strategy import (
    StrategyConfig,
    Blueprint,
    Trigger,
    IndicatorSpec,
)
from tradepose_models.enums import (
    Freq,
    TradeDirection,
    TrendType,
    OrderStrategy,
)
from tradepose_models.indicators import Indicator
import polars as pl

# Create indicator
atr_spec = IndicatorSpec(
    freq=Freq.DAY_1,
    shift=1,
    indicator=Indicator.atr(period=14),
)

# Create trigger
entry_trigger = Trigger(
    name="breakout_entry",
    order_strategy=OrderStrategy.IMMEDIATE_ENTRY,
    priority=1,
    conditions=[pl.col("close") > pl.col("high").shift(1)],
    price_expr=pl.col("close"),
)

# Create blueprint
blueprint = Blueprint(
    name="trend_long",
    direction=TradeDirection.LONG,
    trend_type=TrendType.TREND,
    entry_first=True,
    entry_triggers=[entry_trigger],
    exit_triggers=[...],
)

# Create strategy
strategy = StrategyConfig(
    name="ES_Breakout",
    base_instrument="ES",
    base_freq=Freq.MIN_15,
    note="E-mini S&P breakout strategy",
    indicators=[atr_spec],
    base_blueprint=blueprint,
)

# Save/Load
strategy.save("strategy.json")
loaded = StrategyConfig.load("strategy.json")
```

### Strategy Registry

Manage multiple strategies with `(strategy_name, blueprint_name)` unique keys:

```python
from tradepose_models.strategy import StrategyRegistry, StrategyConfig

# Create registry
registry = StrategyRegistry()

# Add strategy (auto-splits blueprints into separate entries)
strategy = StrategyConfig.load("multi_blueprint_strategy.json")
keys = registry.add(strategy)
# keys = [(BlueprintSelection("MyStrategy", "long_bp"), BlueprintSelection("MyStrategy", "short_bp")]

# Access entries
entry = registry.get("MyStrategy", "long_bp")
print(entry.blueprint.direction)  # TradeDirection.LONG

# Get all configs for backtesting
configs = registry.get_configs()  # List[StrategyConfig] with single blueprints
```

### Portfolio Selection

Create portfolios by selecting from registry:

```python
from tradepose_models.strategy import StrategyRegistry

registry = StrategyRegistry()
registry.add(strategy1)  # 2 blueprints
registry.add(strategy2)  # 3 blueprints

# Create portfolio (selection view)
portfolio = registry.select(
    name="Q1_Momentum",
    selections=[
        ("Strategy1", "momentum_long"),
        ("Strategy1", "momentum_short"),
        ("Strategy2", "trend_follow"),
    ],
    capital=100000,
    currency="USD",
    platform="MT5",
)

# Get configs for BatchTester
configs = portfolio.get_configs(registry)

# Use with BatchTester
from tradepose_client import BatchTester
from tradepose_client.batch import Period

tester = BatchTester(api_key="tp_xxx")
batch = tester.submit(strategies=configs, periods=[Period.Q1(2024)])
batch.wait()
```

---

## Core Concepts

### Strategy Hierarchy

```
StrategyConfig
├── name, base_instrument, base_freq
├── indicators: List[IndicatorSpec]
├── base_blueprint: Blueprint
│   ├── name, direction, trend_type
│   ├── entry_triggers: List[Trigger]
│   │   └── conditions: List[pl.Expr], price_expr: pl.Expr
│   └── exit_triggers: List[Trigger]
└── advanced_blueprints: List[Blueprint]
```

### Registry & Portfolio

```
StrategyRegistry (storage, guarantees uniqueness)
│
│  Key: (strategy_name, blueprint_name)
│
├── add(config) → auto-split blueprints
├── get(name, bp) → RegistryEntry
├── get_configs() → List[StrategyConfig]  ──> for BatchTester
└── select(...) → Portfolio
                     │
                     ▼
              Portfolio (selection view)
              ├── selections: List[(name, bp)]
              ├── capital, currency, platform
              └── get_configs(registry) → configs
```

---

## API Reference

### Enumerations

#### Freq (Time Frequency)
```python
from tradepose_models.enums import Freq

Freq.MIN_1   # "1min"
Freq.MIN_5   # "5min"
Freq.MIN_15  # "15min"
Freq.MIN_30  # "30min"
Freq.HOUR_1  # "1h"
Freq.HOUR_4  # "4h"
Freq.DAY_1   # "1D"
Freq.WEEK_1  # "1W"
Freq.MONTH_1 # "1M"
```

#### TradeDirection
```python
from tradepose_models.enums import TradeDirection

TradeDirection.LONG   # Long trades only
TradeDirection.SHORT  # Short trades only
TradeDirection.BOTH   # Both directions
```

#### TrendType
```python
from tradepose_models.enums import TrendType

TrendType.TREND     # Trend-following
TrendType.RANGE     # Mean-reversion
TrendType.REVERSAL  # Counter-trend
```

#### OrderStrategy
```python
from tradepose_models.enums import OrderStrategy

# Entry
OrderStrategy.IMMEDIATE_ENTRY      # Execute immediately
OrderStrategy.FAVORABLE_DELAY_ENTRY  # Wait for pullback
OrderStrategy.ADVERSE_DELAY_ENTRY   # Wait for breakout

# Exit
OrderStrategy.IMMEDIATE_EXIT  # Exit immediately
OrderStrategy.STOP_LOSS       # Fixed stop loss
OrderStrategy.TAKE_PROFIT     # Fixed profit target
OrderStrategy.TRAILING_STOP   # Dynamic trailing
OrderStrategy.BREAKEVEN       # Move to breakeven
OrderStrategy.TIMEOUT_EXIT    # Time-based exit
```

#### Currency
```python
from tradepose_models.enums import Currency

Currency.USD, Currency.USDT, Currency.TWD
Currency.EUR, Currency.JPY
Currency.BTC, Currency.ETH
Currency.XAU, Currency.TAIEX
```

#### Platform
```python
from tradepose_models.enums import Platform

Platform.MT5      # MetaTrader 5
Platform.BINANCE  # Binance
Platform.SHIOAJI  # Shioaji (Taiwan)
Platform.CCXT     # CCXT unified
```

#### AccountSource
```python
from tradepose_models.enums import AccountSource

AccountSource.FTMO        # tz_offset: 2
AccountSource.IB          # tz_offset: 0
AccountSource.FIVEPERCENT # tz_offset: 2
AccountSource.BINANCE     # tz_offset: 8
AccountSource.SHIOAJI     # tz_offset: 8

# Get timezone offset
offset = AccountSource.FTMO.tz_offset()  # 2
```

### Strategy Models

#### StrategyConfig
```python
from tradepose_models.strategy import StrategyConfig

# Fields
strategy.name              # str: Strategy name
strategy.base_instrument   # str: Trading instrument
strategy.base_freq         # Freq: Base timeframe
strategy.note              # str: Description
strategy.indicators        # List[IndicatorSpec]
strategy.base_blueprint    # Blueprint: Primary blueprint
strategy.advanced_blueprints  # List[Blueprint]: Additional blueprints

# Methods
StrategyConfig.load(path)     # Load from JSON file
strategy.save(path)           # Save to JSON file
strategy.to_json()            # Serialize to JSON string
strategy.to_dict()            # Convert to dict
StrategyConfig.from_api(data) # Parse from API response
```

#### Blueprint
```python
from tradepose_models.strategy import Blueprint

# Fields
blueprint.name           # str: Blueprint name
blueprint.direction      # TradeDirection: LONG/SHORT/BOTH
blueprint.trend_type     # TrendType: TREND/RANGE/REVERSAL
blueprint.entry_first    # bool: Entry signals priority
blueprint.entry_triggers # List[Trigger]
blueprint.exit_triggers  # List[Trigger]
```

#### Trigger
```python
from tradepose_models.strategy import Trigger
import polars as pl

trigger = Trigger(
    name="breakout",
    order_strategy=OrderStrategy.IMMEDIATE_ENTRY,
    priority=1,
    conditions=[
        pl.col("close") > pl.col("high").shift(1),
        pl.col("volume") > pl.col("volume").rolling_mean(20),
    ],
    price_expr=pl.col("close"),
)

# Access Polars expressions directly
expr = trigger.conditions[0]  # pl.Expr
```

#### IndicatorSpec
```python
from tradepose_models.strategy import IndicatorSpec
from tradepose_models.indicators import Indicator

spec = IndicatorSpec(
    freq=Freq.DAY_1,
    shift=1,
    indicator=Indicator.atr(period=14),
)

# Properties
spec.short_name()    # "ATR|14"
spec.display_name()  # "1D_ATR|14_s1"
spec.col()           # pl.col("1D_ATR|14_s1")
```

### Registry Models

#### StrategyRegistry
```python
from tradepose_models.strategy import StrategyRegistry

registry = StrategyRegistry()

# Add strategy (auto-splits blueprints)
keys = registry.add(strategy)  # Returns List[BlueprintSelection]

# Add or replace
keys = registry.add_or_replace(strategy)

# Get entry
entry = registry.get("StrategyName", "blueprint_name")

# Get original strategy (with all blueprints)
original = registry.get_strategy("StrategyName")

# Get all configs (single-blueprint each)
configs = registry.get_configs()

# Remove strategy
removed_count = registry.remove("StrategyName")

# Create portfolio
portfolio = registry.select(
    name="MyPortfolio",
    selections=[("Strat1", "bp1"), ("Strat2", "bp2")],
    capital=100000,
)

# Iteration
for entry in registry:
    print(entry.key)

# Membership
if ("StrategyName", "blueprint") in registry:
    ...

# Length
print(f"Entries: {len(registry)}")
```

#### Portfolio
```python
from tradepose_models.strategy import Portfolio, BlueprintSelection

# Create directly
portfolio = Portfolio(
    name="Q1_Portfolio",
    selections=[BlueprintSelection(strategy_name="Strat1", blueprint_name="bp1")],
    capital=100000,
    currency="USD",
    account_source="FTMO",
    platform="MT5",
)

# Or via registry.select()
portfolio = registry.select(...)

# Get configs for backtesting
configs = portfolio.get_configs(registry)

# Immutable operations (return new instance)
new_portfolio = portfolio.add_selection("Strat2", "bp2")
new_portfolio = portfolio.remove_selection("Strat1", "bp1")

# Properties
portfolio.strategy_names     # List[str] unique names
portfolio.selection_count    # int

# Serialization
portfolio.save("portfolio.json")
loaded = Portfolio.load("portfolio.json")
portfolio.to_json()
portfolio.to_dict()
```

### Indicators

#### Indicator Factory
```python
from tradepose_models.indicators import Indicator

# Moving Averages
Indicator.sma(period=20, column="close")
Indicator.ema(period=20, column="close")
Indicator.smma(period=20, column="close")
Indicator.wma(period=20, column="close")

# Volatility
Indicator.atr(period=14)
Indicator.atr_quantile(period=14, quantile=0.5, window=252)
Indicator.bollinger_bands(period=20, num_std=2.0)

# Trend
Indicator.supertrend(multiplier=3.0, volatility_column="ATR|14")
Indicator.macd(fast=12, slow=26, signal=9)
Indicator.adx(period=14)

# Momentum
Indicator.rsi(period=14)
Indicator.cci(period=20)
Indicator.stochastic(k_period=14, d_period=3)

# Volume Profile
Indicator.market_profile(
    period=30,
    tick_size=0.25,
    value_area_pct=0.70,
)

# Raw OHLCV
Indicator.raw_ohlcv(column="close")
```

---

## Usage Examples

### Multi-Strategy Backtesting

```python
from tradepose_models.strategy import StrategyConfig, StrategyRegistry
from tradepose_client import BatchTester
from tradepose_client.batch import Period

# Setup registry
registry = StrategyRegistry()

# Load multiple strategies
for path in ["strat1.json", "strat2.json", "strat3.json"]:
    strategy = StrategyConfig.load(path)
    registry.add(strategy)

print(f"Registry: {len(registry)} entries")
# Registry: 8 entries (if strategies have multiple blueprints)

# Backtest all
configs = registry.get_configs()
tester = BatchTester(api_key="tp_xxx")
batch = tester.submit(
    strategies=configs,
    periods=[Period.Q1(2024), Period.Q2(2024)],
)
batch.wait()
print(batch.summary())
```

### Portfolio-Based Testing

```python
# Create focused portfolio
momentum_portfolio = registry.select(
    name="Momentum_Suite",
    selections=[
        ("TrendFollower", "momentum_long"),
        ("TrendFollower", "momentum_short"),
        ("BreakoutTrader", "range_breakout"),
    ],
    capital=50000,
    currency="USD",
)

# Test portfolio only
configs = momentum_portfolio.get_configs(registry)
batch = tester.submit(strategies=configs, periods=[Period.Q1(2024)])

# Save portfolio for later
momentum_portfolio.save("momentum_portfolio.json")
```

### Indicator with Struct Fields

```python
from tradepose_models.strategy import IndicatorSpec, Trigger
from tradepose_models.indicators import Indicator
from tradepose_models.enums import Freq, OrderStrategy
import polars as pl

# SuperTrend returns struct with multiple fields
supertrend = IndicatorSpec(
    freq=Freq.DAY_1,
    shift=1,
    indicator=Indicator.supertrend(multiplier=3.0, volatility_column="ATR|14"),
)

# Access struct fields in conditions
trigger = Trigger(
    name="supertrend_long",
    conditions=[
        supertrend.col().struct.field("direction") == 1,  # Long signal
        supertrend.col().struct.field("supertrend") < pl.col("close"),
    ],
    price_expr=pl.col("close"),
    order_strategy=OrderStrategy.IMMEDIATE_ENTRY,
    priority=1,
)
```

---

## File Structure

```
packages/models/src/tradepose_models/
├── __init__.py
├── base.py                 # BaseModel configuration
├── enums/
│   ├── __init__.py
│   ├── freq.py             # Time frequencies
│   ├── trade_direction.py  # LONG/SHORT/BOTH
│   ├── trend_type.py       # TREND/RANGE/REVERSAL
│   ├── order_strategy.py   # Entry/exit strategies
│   ├── currency.py         # Currency types
│   ├── platform.py         # Trading platforms
│   ├── account_source.py   # Brokers/prop firms
│   └── ...
├── strategy/
│   ├── __init__.py
│   ├── config.py           # StrategyConfig
│   ├── blueprint.py        # Blueprint
│   ├── trigger.py          # Trigger
│   ├── indicator_spec.py   # IndicatorSpec
│   ├── registry.py         # StrategyRegistry, RegistryEntry, BlueprintSelection
│   ├── portfolio.py        # Portfolio
│   └── helpers.py          # Factory functions
├── indicators/
│   ├── __init__.py
│   ├── factory.py          # Indicator factory
│   └── ...                 # Indicator type definitions
├── schemas/
│   ├── __init__.py
│   ├── trades.py           # Trades schema
│   ├── performance.py      # Performance schema
│   └── ohlcv.py            # OHLCV schema
└── ...
```

---

## Development

### Running Tests

```bash
# Run models tests
uv run python -m pytest tests/models/ -v

# Run with coverage
uv run python -m pytest tests/models/ --cov=tradepose_models
```

---

## License

MIT License - see [LICENSE](../../LICENSE) file for details.

---

## Support

- **Documentation**: [docs/](../../docs/)
- **Issues**: [GitHub Issues](https://github.com/tradepose/tradepose-python/issues)
