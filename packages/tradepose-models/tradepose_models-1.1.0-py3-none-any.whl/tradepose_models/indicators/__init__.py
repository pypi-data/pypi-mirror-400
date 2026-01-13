"""
Indicator Pydantic Models for Strong Typing

Provides strongly-typed indicator models aligned with Rust backend.
"""

from .base import PolarsExprField
from .factory import Indicator
from .market_profile import (
    AtrQuantileConfig,
    MarketProfileIndicator,
    ProfileShape,
    ProfileShapeConfig,
    create_daily_anchor,
    create_profile_shape_config,
    create_weekly_anchor,
)
from .momentum import CCIIndicator, RSIIndicator, StochasticIndicator
from .moving_average import EMAIndicator, SMAIndicator, SMMAIndicator, WMAIndicator
from .other import BollingerBandsIndicator, RawOhlcvIndicator
from .trend import ADXIndicator, MACDIndicator, SuperTrendIndicator
from .volatility import ATRIndicator, ATRQuantileIndicator

__all__ = [
    # Base
    "PolarsExprField",
    # Moving Average
    "SMAIndicator",
    "EMAIndicator",
    "SMMAIndicator",
    "WMAIndicator",
    # Volatility
    "ATRIndicator",
    "ATRQuantileIndicator",
    # Trend
    "SuperTrendIndicator",
    "MACDIndicator",
    "ADXIndicator",
    # Momentum
    "RSIIndicator",
    "CCIIndicator",
    "StochasticIndicator",
    # Other
    "BollingerBandsIndicator",
    "RawOhlcvIndicator",
    # Market Profile
    "MarketProfileIndicator",
    "AtrQuantileConfig",
    "ProfileShape",
    "ProfileShapeConfig",
    "create_daily_anchor",
    "create_weekly_anchor",
    "create_profile_shape_config",
    # Factory
    "Indicator",
]
