"""
Enhanced OHLCV Schema

Polars schema definition for enhanced OHLCV data with signals and trading context.
"""

import polars as pl

# Enhanced OHLCV Schema
enhanced_ohlcv_schema = {
    "idx": pl.Int64,
    "ts": pl.Datetime("ms"),
    "open": pl.Float64,
    "high": pl.Float64,
    "low": pl.Float64,
    "close": pl.Float64,
    "volume": pl.Float64,
    "gap_type": pl.Int64,
    "gap_points": pl.Float64,
    "gap_range_min": pl.Float64,
    "gap_range_max": pl.Float64,
    "entry_signal": pl.Boolean,
    "exit_signal": pl.Boolean,
    "cleaned_entry_signal": pl.Boolean,
    "cleaned_exit_signal": pl.Boolean,
    "base_entry_price": pl.Float64,
    "base_entry_strategy": pl.Int64,
    "base_exit_price": pl.Float64,
    "base_exit_strategy": pl.Int64,
    "base_position_id": pl.Int64,
    # 巢狀結構統一使用 Struct
    "base_trading_context": pl.Struct(
        [
            pl.Field("bars_in_position", pl.Int64),
            pl.Field("highest_since_entry", pl.Float64),
            pl.Field("lowest_since_entry", pl.Float64),
            pl.Field("position_entry_price", pl.Float64),
        ]
    ),
    # 來自 trigger 自動產生
    # "base_entry": pl.Struct(
    #     [
    #         pl.Field("cond", pl.Boolean),
    #         pl.Field("price", pl.Float64),
    #         pl.Field("strategy", pl.Int64),
    #         pl.Field("priority", pl.Int64),
    #     ]
    # ),
    "advanced_favorable_entry_hypo_price": pl.Float64,
    "advanced_adverse_entry_hypo_price": pl.Float64,
    "advanced_neutral_entry_hypo_price": pl.Float64,
    "advanced_favorable_entry_strategy": pl.Int64,
    "advanced_adverse_entry_strategy": pl.Int64,
    "advanced_neutral_entry_strategy": pl.Int64,
    "advanced_entry_price": pl.Float64,
    "advanced_entry_strategy": pl.Int64,
    "is_entry_gap_filled": pl.Boolean,
    "advanced_cleaned_entry_signal": pl.Boolean,
    "advanced_entry_position_id": pl.Int64,
    "advanced_entry_trading_context": pl.Struct(
        [
            pl.Field("bars_since_advanced_entry", pl.Int64),
            pl.Field("highest_since_advanced_entry", pl.Float64),
            pl.Field("lowest_since_advanced_entry", pl.Float64),
            pl.Field("position_entry_price", pl.Float64),
        ]
    ),
    # 來自 trigger 自動產生
    # "base_exit": pl.Struct(
    #     [
    #         pl.Field("cond", pl.Boolean),
    #         pl.Field("price", pl.Float64),
    #         pl.Field("strategy", pl.Int64),
    #         pl.Field("priority", pl.Int64),
    #     ]
    # ),
    "advanced_favorable_exit_hypo_price": pl.Float64,
    "advanced_adverse_exit_hypo_price": pl.Float64,
    "advanced_neutral_exit_hypo_price": pl.Float64,
    "advanced_favorable_exit_strategy": pl.Int64,
    "advanced_adverse_exit_strategy": pl.Int64,
    "advanced_neutral_exit_strategy": pl.Int64,
    "advanced_exit_price": pl.Float64,
    "advanced_exit_strategy": pl.Int64,
    "is_exit_gap_filled": pl.Boolean,
    "advanced_cleaned_exit_signal": pl.Boolean,
    "advanced_exit_position_id": pl.Int64,
    "advanced_exit_trading_context": pl.Struct(
        [
            pl.Field("bars_since_advanced_entry", pl.Int64),
            pl.Field("highest_since_advanced_entry", pl.Float64),
            pl.Field("lowest_since_advanced_entry", pl.Float64),
            pl.Field("position_entry_price", pl.Float64),
        ]
    ),
    "is_entry_valid": pl.Boolean,
    "entry_rejection_reason": pl.Utf8,
    "validated_entry_signal": pl.Boolean,
    "validated_exit_signal": pl.Boolean,
    "final_position_id": pl.Int64,
    "final_trading_context": pl.Struct(
        [
            pl.Field("bars_in_position", pl.Int64),
            pl.Field("highest_since_entry", pl.Float64),
            pl.Field("lowest_since_entry", pl.Float64),
            pl.Field("position_entry_price", pl.Float64),
        ]
    ),
    "strategy_name": pl.Utf8,
    "blueprint_name": pl.Utf8,
}
