"""
Export Request Models

Provides models for on-demand OHLCV export requests.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OnDemandOhlcvRequest(BaseModel):
    """On-Demand OHLCV 導出請求（與 Rust OnDemandOhlcvRequest struct 一致）

    特點：
    - 無需預先註冊策略
    - 直接指定指標規格即可導出
    - 適用於快速探索指標、外部數據分析

    Example:
        >>> from tradepose_models import create_indicator_spec, Indicator, Freq
        >>>
        >>> # 定義指標
        >>> sma_spec = create_indicator_spec(Freq.HOUR_1, Indicator.sma(20), shift=1)
        >>> atr_spec = create_indicator_spec(Freq.HOUR_1, Indicator.atr(14), shift=1)
        >>>
        >>> # 創建請求
        >>> request = OnDemandOhlcvRequest(
        ...     base_instrument="TXFR1",
        ...     base_freq="1min",
        ...     indicator_specs=[
        ...         sma_spec.model_dump(exclude_none=True),
        ...         atr_spec.model_dump(exclude_none=True)
        ...     ],
        ...     start_date="2025-01-01T00:00:00",
        ...     end_date="2025-01-02T23:59:59"
        ... )
    """

    base_instrument: str = Field(
        ..., description="基礎商品 ID (例如 'TXFR1', 'TXF_M1_SHIOAJI_FUTURE')"
    )
    base_freq: str = Field(
        ..., description="基礎頻率 ('1min', '5min', '15min', '1h', '4h', '1D' 等)"
    )
    indicator_specs: List[Dict[str, Any]] = Field(
        ..., description="指標規格列表 (IndicatorSpec JSON 數組)", min_length=1
    )
    start_date: Optional[str] = Field(
        None, description="開始時間 (ISO 8601 格式，例如 '2025-01-01T00:00:00')"
    )
    end_date: Optional[str] = Field(None, description="結束時間 (ISO 8601 格式，預設為當前時間)")
