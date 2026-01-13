"""
Enumerations for TradePose platform

All enums are aligned with Rust backend types for JSON serialization.
"""

from .account_source import AccountSource
from .broker_type import BrokerType
from .currency import Currency
from .engagement_phase import EngagementPhase
from .execution_mode import ExecutionMode
from .export_type import ExportType
from .freq import Freq
from .indicator_type import IndicatorType
from .operation_type import OperationType
from .order_strategy import OrderStrategy
from .orderbook_event_type import OrderbookEventType
from .persist_mode import PersistMode
from .stream import RedisStream
from .task_status import TaskStatus
from .trade_direction import TradeDirection
from .trend_type import TrendType
from .weekday import Weekday

# Backwards compatibility alias (deprecated, use BrokerType instead)
Platform = BrokerType

__all__ = [
    "AccountSource",
    "BrokerType",
    "Currency",
    "EngagementPhase",
    "ExecutionMode",
    "ExportType",
    "Freq",
    "IndicatorType",
    "OperationType",
    "OrderStrategy",
    "OrderbookEventType",
    "PersistMode",
    "Platform",  # Deprecated alias for BrokerType
    "RedisStream",
    "TaskStatus",
    "TradeDirection",
    "TrendType",
    "Weekday",
]
