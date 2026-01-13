"""Broker type enumeration for trading platforms."""

from enum import StrEnum


class BrokerType(StrEnum):
    """Supported broker types for trading platforms.

    This enum represents the different trading platforms/brokers that can be used.
    Use this instead of the deprecated Platform enum.

    Values are lowercase to match database enum values.
    """

    MT5 = "mt5"
    BINANCE = "binance"
    OKX = "okx"
    SHIOAJI = "shioaji"  # Taiwan Sinopac
    CCXT = "ccxt"  # Generic CCXT adapter
    INTERACTIVE_BROKERS = "ib"
    TRADEPOSE_MOCK = "tradepose_mock"  # Mock broker for testing
