"""Operation type enum for task operations."""

from enum import Enum


class OperationType(str, Enum):
    """Task operation types for Gateway."""

    # Backtest operations
    BACKTEST_RESULTS = "backtest-results"
    ENHANCED_OHLCV = "enhanced-ohlcv"
    LATEST_TRADES = "latest-trades"
    ON_DEMAND_OHLCV = "on-demand-ohlcv"

    # Strategy operations
    REGISTER_STRATEGY = "register_strategy"
    LIST_STRATEGIES = "list_strategies"
    GET_STRATEGY = "get_strategy"
    DELETE_STRATEGY = "delete_strategy"
