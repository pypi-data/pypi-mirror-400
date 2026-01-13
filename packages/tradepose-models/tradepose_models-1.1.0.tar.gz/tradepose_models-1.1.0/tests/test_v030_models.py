"""Unit tests for v0.3.0 models.

Tests for:
- Portfolio (instrument_mapping field)
- StrategyEntity, BlueprintEntity
- Engagement, OrderbookEntry
- AccountPortfolioBinding
- StrategyPerformance
"""

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from tradepose_models.broker import AccountPortfolioBinding
from tradepose_models.enums import (
    EngagementPhase,
    ExecutionMode,
    Freq,
    OrderbookEventType,
    TradeDirection,
    TrendType,
)
from tradepose_models.strategy import (
    BlueprintEntity,
    Portfolio,
    StrategyEntity,
    StrategyPerformance,
)
from tradepose_models.trading import Engagement, OrderbookEntry
from tradepose_models.trading.orders import OrderSide, OrderStatus, OrderType


class TestPortfolioInstrumentMapping:
    """Tests for Portfolio.instrument_mapping field."""

    def test_instrument_mapping_optional(self):
        """Test that instrument_mapping is optional."""
        portfolio = Portfolio(name="test_portfolio")
        assert portfolio.instrument_mapping is None

    def test_instrument_mapping_set(self):
        """Test setting instrument_mapping."""
        portfolio = Portfolio(
            name="test_portfolio",
            instrument_mapping={"BTC": "BTCUSDT", "XAU": "XAUUSD"},
        )
        assert portfolio.instrument_mapping == {"BTC": "BTCUSDT", "XAU": "XAUUSD"}

    def test_instrument_mapping_serialization(self):
        """Test instrument_mapping JSON serialization."""
        portfolio = Portfolio(
            name="test_portfolio",
            capital=100000,
            currency="USD",
            instrument_mapping={"BTC": "BTCUSDT"},
        )
        data = portfolio.to_dict()
        assert data["instrument_mapping"] == {"BTC": "BTCUSDT"}

    def test_instrument_mapping_from_json(self):
        """Test creating Portfolio from JSON with instrument_mapping."""
        json_str = '{"name": "test", "instrument_mapping": {"ETH": "ETHUSDT"}}'
        portfolio = Portfolio.from_api(json_str)
        assert portfolio.instrument_mapping == {"ETH": "ETHUSDT"}


class TestStrategyEntity:
    """Tests for StrategyEntity model."""

    def test_create_strategy_entity(self):
        """Test creating a StrategyEntity."""
        now = datetime.utcnow()
        entity = StrategyEntity(
            id=uuid4(),
            user_id=uuid4(),
            name="test_strategy",
            base_instrument="BTC",
            base_freq=Freq.MIN_15,
            note="Test note",
            created_at=now,
            updated_at=now,
        )
        assert entity.name == "test_strategy"
        assert entity.base_instrument == "BTC"
        assert entity.is_archived is False

    def test_strategy_entity_with_indicators(self):
        """Test StrategyEntity with indicators."""
        now = datetime.utcnow()
        entity = StrategyEntity(
            id=uuid4(),
            user_id=uuid4(),
            name="test_strategy",
            base_instrument="XAU",
            base_freq=Freq.HOUR_1,
            note="",
            indicators=[],
            created_at=now,
            updated_at=now,
        )
        assert entity.indicators == []


class TestBlueprintEntity:
    """Tests for BlueprintEntity model."""

    def test_create_blueprint_entity(self):
        """Test creating a BlueprintEntity."""
        now = datetime.utcnow()
        entity = BlueprintEntity(
            id=uuid4(),
            strategy_id=uuid4(),
            name="test_blueprint",
            direction=TradeDirection.LONG,
            trend_type=TrendType.TREND,
            entry_first=True,
            note="Test",
            created_at=now,
            updated_at=now,
        )
        assert entity.name == "test_blueprint"
        assert entity.direction == TradeDirection.LONG
        assert entity.is_base is False
        assert entity.is_archived is False

    def test_blueprint_entity_direction_from_string(self):
        """Test BlueprintEntity direction field validator."""
        now = datetime.utcnow()
        entity = BlueprintEntity(
            id=uuid4(),
            strategy_id=uuid4(),
            name="test",
            direction="Long",  # String should be converted (case-sensitive)
            trend_type="Trend",  # String should be converted (case-sensitive)
            entry_first=True,
            note="",
            created_at=now,
            updated_at=now,
        )
        assert entity.direction == TradeDirection.LONG
        assert entity.trend_type == TrendType.TREND


class TestEngagement:
    """Tests for Engagement model."""

    def test_create_engagement(self):
        """Test creating an Engagement."""
        now = datetime.utcnow()
        engagement = Engagement(
            id=uuid4(),
            user_id=uuid4(),
            account_id=uuid4(),
            binding_id=uuid4(),
            portfolio_id=uuid4(),
            blueprint_id=uuid4(),
            trade_id=uuid4(),
            created_at=now,
            updated_at=now,
        )
        assert engagement.phase == EngagementPhase.PENDING
        assert engagement.is_pending_phase is True
        assert engagement.is_holding_phase is False
        assert engagement.is_closed_phase is False

    def test_engagement_phase_transitions(self):
        """Test engagement phase properties."""
        now = datetime.utcnow()
        base_kwargs = {
            "id": uuid4(),
            "user_id": uuid4(),
            "account_id": uuid4(),
            "binding_id": uuid4(),
            "portfolio_id": uuid4(),
            "blueprint_id": uuid4(),
            "trade_id": uuid4(),
            "created_at": now,
            "updated_at": now,
        }

        # Test PENDING
        engagement = Engagement(**base_kwargs, phase=EngagementPhase.PENDING)
        assert engagement.is_pending_phase is True

        # Test HOLDING (position open)
        engagement = Engagement(**base_kwargs, phase=EngagementPhase.HOLDING)
        assert engagement.is_holding_phase is True

        # Test CLOSED
        engagement = Engagement(**base_kwargs, phase=EngagementPhase.CLOSED)
        assert engagement.is_closed_phase is True

        # Test terminal states
        assert engagement.is_terminal is True

        # Test FAILED
        engagement = Engagement(**base_kwargs, phase=EngagementPhase.FAILED)
        assert engagement.is_failed_phase is True
        assert engagement.is_terminal is True

        # Test CANCELLED
        engagement = Engagement(**base_kwargs, phase=EngagementPhase.CANCELLED)
        assert engagement.is_cancelled_phase is True
        assert engagement.is_terminal is True

        # Test EXIT_FAILED
        engagement = Engagement(**base_kwargs, phase=EngagementPhase.EXIT_FAILED)
        assert engagement.is_exit_failed_phase is True
        assert engagement.needs_intervention is True


class TestOrderbookEntry:
    """Tests for OrderbookEntry model."""

    def test_create_orderbook_entry(self):
        """Test creating an OrderbookEntry."""
        now = datetime.utcnow()
        entry = OrderbookEntry(
            id=uuid4(),
            user_id=uuid4(),
            engagement_id=uuid4(),
            event_type=OrderbookEventType.ORDER_CREATED,
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("0.1"),
            broker_order_id="123456",
            status=OrderStatus.NEW,
            created_at=now,
            updated_at=now,
        )
        assert entry.event_type == OrderbookEventType.ORDER_CREATED
        assert entry.filled_quantity == Decimal("0")

    def test_orderbook_entry_properties(self):
        """Test OrderbookEntry computed properties."""
        now = datetime.utcnow()
        entry = OrderbookEntry(
            id=uuid4(),
            user_id=uuid4(),
            engagement_id=uuid4(),
            event_type=OrderbookEventType.PARTIAL_FILL,
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("1.0"),
            filled_quantity=Decimal("0.3"),
            price=Decimal("50000"),
            filled_price=Decimal("49900"),
            broker_order_id="123456",
            status=OrderStatus.PARTIALLY_FILLED,
            created_at=now,
            updated_at=now,
        )
        assert entry.is_partial is True
        assert entry.is_filled is False
        assert entry.remaining_quantity == Decimal("0.7")


class TestAccountPortfolioBinding:
    """Tests for AccountPortfolioBinding model."""

    def test_create_binding(self):
        """Test creating an AccountPortfolioBinding."""
        now = datetime.utcnow()
        binding = AccountPortfolioBinding(
            id=uuid4(),
            user_id=uuid4(),
            account_id=uuid4(),
            portfolio_id=uuid4(),
            created_at=now,
            updated_at=now,
        )
        assert binding.execution_mode == ExecutionMode.PRICE_PRIORITY
        assert binding.capital_override is None
        assert binding.is_price_priority is True
        assert binding.is_signal_priority is False

    def test_binding_with_override(self):
        """Test binding with capital override."""
        now = datetime.utcnow()
        binding = AccountPortfolioBinding(
            id=uuid4(),
            user_id=uuid4(),
            account_id=uuid4(),
            portfolio_id=uuid4(),
            capital_override=Decimal("50000"),
            execution_mode=ExecutionMode.SIGNAL_PRIORITY,
            created_at=now,
            updated_at=now,
        )
        assert binding.capital_override == Decimal("50000")
        assert binding.is_signal_priority is True


class TestStrategyPerformance:
    """Tests for StrategyPerformance model."""

    def test_create_performance(self):
        """Test creating a StrategyPerformance."""
        now = datetime.utcnow()
        perf = StrategyPerformance(
            strategy_name="test_strategy",
            blueprint_name="test_blueprint",
            user_id=uuid4(),
            instrument="XAUUSD",
            win_rate=0.65,
            avg_pnl_pct=2.5,
            mae_q90=5.0,
            mfe_q90=8.0,
            recovery_factor=1.5,
            expected_loss_per_contract=Decimal("40000"),
            quote_currency="USD",
            contract_size=Decimal("100"),
            updated_at=now,
        )
        assert perf.win_rate == 0.65
        assert perf.expected_loss_per_contract == Decimal("40000")

    def test_position_size_calculation(self):
        """Test position size calculation."""
        now = datetime.utcnow()
        perf = StrategyPerformance(
            strategy_name="test",
            blueprint_name="bp",
            user_id=uuid4(),
            instrument="XAUUSD",
            win_rate=0.6,
            avg_pnl_pct=2.0,
            mae_q90=5.0,
            mfe_q90=8.0,
            recovery_factor=1.5,
            expected_loss_per_contract=Decimal("40000"),
            quote_currency="USD",
            contract_size=Decimal("100"),
            updated_at=now,
        )
        # 80000 / 40000 = 2 contracts
        qty = perf.calculate_position_size(Decimal("80000"))
        assert qty == Decimal("2")

    def test_position_size_zero_loss(self):
        """Test position size with zero expected loss returns 0."""
        now = datetime.utcnow()
        perf = StrategyPerformance(
            strategy_name="test",
            blueprint_name="bp",
            user_id=uuid4(),
            instrument="TEST",
            win_rate=0.5,
            avg_pnl_pct=0.0,
            mae_q90=0.0,
            mfe_q90=0.0,
            recovery_factor=0.0,
            expected_loss_per_contract=Decimal("0"),
            quote_currency="USD",
            contract_size=Decimal("1"),
            updated_at=now,
        )
        qty = perf.calculate_position_size(Decimal("100000"))
        assert qty == Decimal("0")
