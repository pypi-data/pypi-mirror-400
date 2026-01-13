"""
Order strategy enumeration
"""

from enum import Enum


class OrderStrategy(str, Enum):
    """
    Order strategy enum (aligned with Rust OrderStrategy enum)

    Used to specify the execution strategy for entry/exit triggers.

    Rust mapping:
    - Rust: OrderStrategy::ImmediateEntry      → Python: OrderStrategy.IMMEDIATE_ENTRY      (u32: 0)
    - Rust: OrderStrategy::FavorableDelayEntry → Python: OrderStrategy.FAVORABLE_DELAY_ENTRY (u32: 1)
    - Rust: OrderStrategy::AdverseDelayEntry   → Python: OrderStrategy.ADVERSE_DELAY_ENTRY   (u32: 2)
    - Rust: OrderStrategy::ImmediateExit       → Python: OrderStrategy.IMMEDIATE_EXIT        (u32: 3)
    - Rust: OrderStrategy::StopLoss            → Python: OrderStrategy.STOP_LOSS             (u32: 4)
    - Rust: OrderStrategy::TakeProfit          → Python: OrderStrategy.TAKE_PROFIT           (u32: 5)
    - Rust: OrderStrategy::TrailingStop        → Python: OrderStrategy.TRAILING_STOP         (u32: 6)
    - Rust: OrderStrategy::Breakeven           → Python: OrderStrategy.BREAKEVEN             (u32: 7)
    - Rust: OrderStrategy::TimeoutExit         → Python: OrderStrategy.TIMEOUT_EXIT          (u32: 8)

    Entry Strategies:
        IMMEDIATE_ENTRY: Immediate entry on signal (required for Base Blueprint)
        FAVORABLE_DELAY_ENTRY: Wait for favorable price (pullback/retracement)
        ADVERSE_DELAY_ENTRY: Wait for breakout/aggressive entry

    Exit Strategies:
        IMMEDIATE_EXIT: Immediate exit on signal (required for Base Blueprint)
        STOP_LOSS: Fixed stop loss
        TAKE_PROFIT: Fixed take profit
        TRAILING_STOP: Dynamic trailing stop
        BREAKEVEN: Move stop to breakeven after profit
        TIMEOUT_EXIT: Exit after time limit
    """

    IMMEDIATE_ENTRY = "ImmediateEntry"
    FAVORABLE_DELAY_ENTRY = "FavorableDelayEntry"
    ADVERSE_DELAY_ENTRY = "AdverseDelayEntry"
    IMMEDIATE_EXIT = "ImmediateExit"
    STOP_LOSS = "StopLoss"
    TAKE_PROFIT = "TakeProfit"
    TRAILING_STOP = "TrailingStop"
    BREAKEVEN = "Breakeven"
    TIMEOUT_EXIT = "TimeoutExit"
