"""
Performance Schema

Polars schema definition for performance metrics from backtest results.
"""

import polars as pl

# Performance Schema (from backtest-results export)
# Updated to match actual API response
performance_schema = {
    # Identifiers
    "strategy_name": pl.Utf8,
    "blueprint_name": pl.Utf8,
    "metric_type": pl.Utf8,  # "pnl_pct" or "pnl"
    # Basic trade statistics
    "trades": pl.UInt32,  # Total number of trades (renamed from total_trades)
    "win_ratio": pl.Float64,  # Win rate (renamed from win_rate)
    # Time information
    "first_entry_time": pl.Datetime("ms"),
    "last_entry_time": pl.Datetime("ms"),
    "last_exit_time": pl.Datetime("ms"),
    # Performance metrics
    "total": pl.Float64,  # Total PnL (renamed from total_pnl)
    "expect_payoff": pl.Float64,  # Expected payoff per trade
    "pnl_std": pl.Float64,  # Standard deviation of PnL
    # Risk metrics
    "profit_factor": pl.Float64,
    "sharpe_ratio": pl.Float64,
    "sortino_ratio": pl.Float64,
    "recovery_factor": pl.Float64,
    # MAE/MFE risk analysis
    "risk_mae_pct_p75": pl.Float64,  # 75th percentile MAE (risk management)
    "risk_mae_pct_conservative": pl.Float64,  # Conservative MAE estimate
    "risk_mae_pct_p95": pl.Float64,  # 95th percentile MAE (worst case)
    "g_mfe_after_mae_pct": pl.Float64,  # Global MFE after MAE
    # Advanced metrics
    "kelly": pl.Float64,  # Kelly criterion
    "sqn": pl.Float64,  # System Quality Number
}
