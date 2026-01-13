"""
Trades Schema

Polars schema definition for trades data from backtest results or latest trades export.
"""

import polars as pl

# Trades Schema (from backtest-results or latest-trades export)
# Complete schema matching API response with MAE/MFE fields
trades_schema = {
    # Position identifiers
    "final_position_id": pl.UInt32,
    "position_id": pl.UInt32,
    "direction": pl.Int32,  # -1 for Short, 1 for Long
    "status": pl.Boolean,  # false = closed, true = open
    # Entry details
    "entry_idx": pl.UInt32,
    "entry_time": pl.Datetime("ms"),
    "entry_price": pl.Float64,
    "entry_reason": pl.UInt32,
    "favorable_entry_hypo_price": pl.Float64,
    "adverse_entry_hypo_price": pl.Float64,
    "favorable_entry_strategy": pl.UInt32,
    "adverse_entry_strategy": pl.UInt32,
    # Exit details
    "exit_idx": pl.UInt32,
    "exit_time": pl.Datetime("ms"),
    "exit_price": pl.Float64,
    "exit_reason": pl.UInt32,
    "favorable_exit_hypo_price": pl.Float64,
    "adverse_exit_hypo_price": pl.Float64,
    "favorable_exit_strategy": pl.UInt32,
    "adverse_exit_strategy": pl.UInt32,
    # Holding period
    "holding_seconds": pl.Int64,
    "holding_bars": pl.UInt32,
    # MAE/MFE metrics (Maximum Adverse/Favorable Excursion)
    "g_mfe": pl.Float64,  # Global Maximum Favorable Excursion
    "mae": pl.Float64,  # Maximum Adverse Excursion
    "mfe": pl.Float64,  # Maximum Favorable Excursion
    "mae_lv1": pl.Float64,  # MAE Level 1
    "mhl": pl.Float64,  # Maximum High/Low
    # MAE/MFE indices (bar index where each occurred)
    "g_mfe_idx": pl.UInt32,
    "mae_idx": pl.UInt32,
    "mfe_idx": pl.UInt32,
    "mae_lv1_idx": pl.UInt32,
    "mhl_idx": pl.UInt32,
    # Volatility at each key point (typically ATR)
    "entry_volatility": pl.Float64,
    "exit_volatility": pl.Float64,
    "g_mfe_volatility": pl.Float64,
    "mae_volatility": pl.Float64,
    "mfe_volatility": pl.Float64,
    "mae_lv1_volatility": pl.Float64,
    "mhl_volatility": pl.Float64,
    # P&L metrics
    "pnl": pl.Float64,  # Absolute profit/loss
    "pnl_pct": pl.Float64,  # Percentage profit/loss
    # Metadata
    "strategy_name": pl.Utf8,
    "blueprint_name": pl.Utf8,
}
