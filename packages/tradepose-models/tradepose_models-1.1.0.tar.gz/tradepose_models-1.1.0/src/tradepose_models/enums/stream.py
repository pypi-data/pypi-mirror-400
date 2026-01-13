"""Redis Stream name enums."""

from enum import Enum


class RedisStream(str, Enum):
    """Redis Stream names used across the platform."""

    BACKTEST_TASKS = "backtest:tasks"
    DATAFEED_TASKS = "datafeed:tasks"
    TRADER_COMMANDS = (
        "trader:commands"  # Base, actual format: trader:commands:{user_id}:{node_seq}:{slot_idx}
    )
    ORDER_EVENTS = "order:events"  # Base, actual format: order:events:{user_id}:{account_id}
