"""Unit tests for Order Event models.

Tests for:
- EntryOrderEvent
- ExitOrderEvent
"""

from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError
from tradepose_models.events import EntryOrderEvent, ExitOrderEvent
from tradepose_models.trading.orders import OrderSide, OrderType


class TestEntryOrderEvent:
    """Tests for EntryOrderEvent model."""

    def test_create_with_all_fields(self):
        """Test creating EntryOrderEvent with all fields."""
        engagement_id = uuid4()
        account_id = uuid4()

        event = EntryOrderEvent(
            engagement_id=engagement_id,
            account_id=account_id,
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            quantity=Decimal("0.1"),
            order_type=OrderType.MARKET,
            entry_price=Decimal("50000"),
            sl_price=Decimal("49000"),
            tp_price=Decimal("52000"),
        )

        assert event.engagement_id == engagement_id
        assert event.account_id == account_id
        assert event.symbol == "BTCUSDT"
        assert event.side == OrderSide.BUY
        assert event.quantity == Decimal("0.1")
        assert event.order_type == OrderType.MARKET
        assert event.entry_price == Decimal("50000")
        assert event.sl_price == Decimal("49000")
        assert event.tp_price == Decimal("52000")

    def test_create_without_optional_fields(self):
        """Test creating EntryOrderEvent without SL/TP."""
        event = EntryOrderEvent(
            engagement_id=uuid4(),
            account_id=uuid4(),
            symbol="EURUSD",
            side=OrderSide.SELL,
            quantity=Decimal("1.0"),
            order_type=OrderType.LIMIT,
            entry_price=Decimal("1.0850"),
        )

        assert event.sl_price is None
        assert event.tp_price is None

    def test_to_redis_dict_with_all_fields(self):
        """Test to_redis_dict with all fields populated."""
        engagement_id = uuid4()
        account_id = uuid4()

        event = EntryOrderEvent(
            engagement_id=engagement_id,
            account_id=account_id,
            symbol="US100",
            side=OrderSide.BUY,
            quantity=Decimal("0.5"),
            order_type=OrderType.MARKET,
            entry_price=Decimal("18500.50"),
            sl_price=Decimal("18400"),
            tp_price=Decimal("18700"),
        )

        redis_dict = event.to_redis_dict()

        assert redis_dict["event_type"] == "entry"
        assert redis_dict["engagement_id"] == str(engagement_id)
        assert redis_dict["account_id"] == str(account_id)
        assert redis_dict["symbol"] == "US100"
        assert redis_dict["side"] == "buy"
        assert redis_dict["quantity"] == "0.5"
        assert redis_dict["order_type"] == "market"
        assert redis_dict["entry_price"] == "18500.50"
        assert redis_dict["sl_price"] == "18400"
        assert redis_dict["tp_price"] == "18700"

    def test_to_redis_dict_without_sl_tp(self):
        """Test to_redis_dict when SL/TP are None."""
        event = EntryOrderEvent(
            engagement_id=uuid4(),
            account_id=uuid4(),
            symbol="XAUUSD",
            side=OrderSide.BUY,
            quantity=Decimal("0.01"),
            order_type=OrderType.MARKET,
            entry_price=Decimal("2050.00"),
        )

        redis_dict = event.to_redis_dict()

        assert redis_dict["sl_price"] == ""
        assert redis_dict["tp_price"] == ""

    def test_required_fields_validation(self):
        """Test that required fields raise validation error when missing."""
        with pytest.raises(ValidationError) as exc_info:
            EntryOrderEvent(
                engagement_id=uuid4(),
                account_id=uuid4(),
                symbol="BTCUSDT",
                side=OrderSide.BUY,
                quantity=Decimal("0.1"),
                order_type=OrderType.MARKET,
                # missing entry_price
            )

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("entry_price",)
        assert errors[0]["type"] == "missing"

    def test_sell_side(self):
        """Test EntryOrderEvent with SELL side."""
        event = EntryOrderEvent(
            engagement_id=uuid4(),
            account_id=uuid4(),
            symbol="EURUSD",
            side=OrderSide.SELL,
            quantity=Decimal("2.0"),
            order_type=OrderType.MARKET,
            entry_price=Decimal("1.0900"),
        )

        redis_dict = event.to_redis_dict()
        assert redis_dict["side"] == "sell"

    def test_limit_order_type(self):
        """Test EntryOrderEvent with LIMIT order type."""
        event = EntryOrderEvent(
            engagement_id=uuid4(),
            account_id=uuid4(),
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            quantity=Decimal("0.5"),
            order_type=OrderType.LIMIT,
            entry_price=Decimal("48000"),
        )

        redis_dict = event.to_redis_dict()
        assert redis_dict["order_type"] == "limit"


class TestExitOrderEvent:
    """Tests for ExitOrderEvent model."""

    def test_create_with_all_fields(self):
        """Test creating ExitOrderEvent with all fields."""
        engagement_id = uuid4()
        account_id = uuid4()

        event = ExitOrderEvent(
            engagement_id=engagement_id,
            account_id=account_id,
            symbol="BTCUSDT",
            side=OrderSide.SELL,
            quantity=Decimal("0.1"),
            order_type=OrderType.MARKET,
        )

        assert event.engagement_id == engagement_id
        assert event.account_id == account_id
        assert event.symbol == "BTCUSDT"
        assert event.side == OrderSide.SELL
        assert event.quantity == Decimal("0.1")
        assert event.order_type == OrderType.MARKET

    def test_default_order_type_is_market(self):
        """Test that default order_type is MARKET."""
        event = ExitOrderEvent(
            engagement_id=uuid4(),
            account_id=uuid4(),
            symbol="EURUSD",
            side=OrderSide.BUY,
            quantity=Decimal("1.0"),
        )

        assert event.order_type == OrderType.MARKET

    def test_to_redis_dict(self):
        """Test to_redis_dict conversion."""
        engagement_id = uuid4()
        account_id = uuid4()

        event = ExitOrderEvent(
            engagement_id=engagement_id,
            account_id=account_id,
            symbol="US100",
            side=OrderSide.SELL,
            quantity=Decimal("0.5"),
        )

        redis_dict = event.to_redis_dict()

        assert redis_dict["event_type"] == "exit"
        assert redis_dict["engagement_id"] == str(engagement_id)
        assert redis_dict["account_id"] == str(account_id)
        assert redis_dict["symbol"] == "US100"
        assert redis_dict["side"] == "sell"
        assert redis_dict["quantity"] == "0.5"
        assert redis_dict["order_type"] == "market"

    def test_exit_with_buy_side(self):
        """Test ExitOrderEvent with BUY side (closing short position)."""
        event = ExitOrderEvent(
            engagement_id=uuid4(),
            account_id=uuid4(),
            symbol="XAUUSD",
            side=OrderSide.BUY,
            quantity=Decimal("0.02"),
        )

        redis_dict = event.to_redis_dict()
        assert redis_dict["side"] == "buy"

    def test_required_fields_validation(self):
        """Test that required fields raise validation error when missing."""
        with pytest.raises(ValidationError) as exc_info:
            ExitOrderEvent(
                engagement_id=uuid4(),
                account_id=uuid4(),
                # missing symbol, side, quantity
            )

        errors = exc_info.value.errors()
        assert len(errors) == 3
        error_fields = {e["loc"][0] for e in errors}
        assert "symbol" in error_fields
        assert "side" in error_fields
        assert "quantity" in error_fields

    def test_exit_no_sl_tp_fields(self):
        """Test that ExitOrderEvent does not have sl_price or tp_price."""
        event = ExitOrderEvent(
            engagement_id=uuid4(),
            account_id=uuid4(),
            symbol="EURUSD",
            side=OrderSide.SELL,
            quantity=Decimal("1.0"),
        )

        # ExitOrderEvent should not have sl_price or tp_price attributes
        assert not hasattr(event, "sl_price") or event.model_fields.get("sl_price") is None
        assert not hasattr(event, "tp_price") or event.model_fields.get("tp_price") is None

        # Redis dict should not have sl_price or tp_price
        redis_dict = event.to_redis_dict()
        assert "sl_price" not in redis_dict
        assert "tp_price" not in redis_dict


class TestOrderEventInteroperability:
    """Tests for interoperability between Entry and Exit events."""

    def test_entry_exit_pair_consistency(self):
        """Test that entry and exit events can share engagement_id."""
        engagement_id = uuid4()
        account_id = uuid4()

        entry = EntryOrderEvent(
            engagement_id=engagement_id,
            account_id=account_id,
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            quantity=Decimal("0.5"),
            order_type=OrderType.MARKET,
            entry_price=Decimal("50000"),
        )

        # Exit should use same engagement_id and account_id
        exit_event = ExitOrderEvent(
            engagement_id=engagement_id,
            account_id=account_id,
            symbol="BTCUSDT",
            side=OrderSide.SELL,  # Opposite of entry
            quantity=Decimal("0.5"),  # Same quantity
        )

        assert entry.engagement_id == exit_event.engagement_id
        assert entry.account_id == exit_event.account_id
        assert entry.symbol == exit_event.symbol
        assert entry.quantity == exit_event.quantity

    def test_redis_dict_values_are_strings(self):
        """Test that all Redis dict values are strings (Redis requirement)."""
        entry = EntryOrderEvent(
            engagement_id=uuid4(),
            account_id=uuid4(),
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            quantity=Decimal("0.5"),
            order_type=OrderType.MARKET,
            entry_price=Decimal("50000"),
            sl_price=Decimal("49000"),
            tp_price=Decimal("52000"),
        )

        redis_dict = entry.to_redis_dict()
        for key, value in redis_dict.items():
            assert isinstance(value, str), f"Field {key} should be string, got {type(value)}"

        exit_event = ExitOrderEvent(
            engagement_id=uuid4(),
            account_id=uuid4(),
            symbol="BTCUSDT",
            side=OrderSide.SELL,
            quantity=Decimal("0.5"),
        )

        redis_dict = exit_event.to_redis_dict()
        for key, value in redis_dict.items():
            assert isinstance(value, str), f"Field {key} should be string, got {type(value)}"
