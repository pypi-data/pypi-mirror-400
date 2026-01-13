"""
Export type enumeration for export tasks
"""

from enum import Enum


class ExportType(int, Enum):
    """導出類型枚舉（與 Rust ExportType enum 一致）

    對應 Rust 的 ExportType enum，定義支援的導出格式

    Rust 對應關係（#[repr(i16)]）:
    - Rust: ExportType::BacktestResults = 0 → Python: ExportType.BACKTEST_RESULTS = 0
    - Rust: ExportType::LatestTrades    = 1 → Python: ExportType.LATEST_TRADES    = 1
    - Rust: ExportType::EnhancedOhlcv   = 2 → Python: ExportType.ENHANCED_OHLCV   = 2
    - Rust: ExportType::OnDemandOhlcv   = 3 → Python: ExportType.ON_DEMAND_OHLCV  = 3
    """

    BACKTEST_RESULTS = 0  # 完整回測結果（trades + performance）
    LATEST_TRADES = 1  # 最新持倉狀態
    ENHANCED_OHLCV = 2  # 增強 OHLCV（包含所有指標和信號）
    ON_DEMAND_OHLCV = 3  # 按需 OHLCV（無需註冊策略）
