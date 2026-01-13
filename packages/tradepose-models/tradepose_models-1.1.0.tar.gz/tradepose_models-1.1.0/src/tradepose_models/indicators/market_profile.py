"""
Market Profile Indicator Model and Configuration

Market Profile indicator with anchor config and shape recognition aligned with Rust backend.
"""

from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from ..enums import Weekday


class ProfileShape(str, Enum):
    """Market Profile 形狀分類（對應 Rust ProfileShape enum）

    用於識別 TPO 分布的市場結構模式。

    Shapes:
        P_SHAPED: P型（快速上漲 + 高位盤整，看空信號）
        B_SHAPED: b型（快速下跌 + 低位盤整，看多信號）
        B_DOUBLE_DISTRIBUTION: B型雙峰（區間交易）
        TREND_DAY: 趨勢日（持續單向移動，順勢交易）
        NORMAL: 正態分布（對稱分布，區間交易）
        UNDEFINED: 無法分類

    Example:
        >>> from tradepose_models.indicators.market_profile import ProfileShape
        >>> shape = ProfileShape.P_SHAPED
        >>> print(shape.value)  # "p_shaped"
    """

    P_SHAPED = "p_shaped"
    B_SHAPED = "b_shaped"
    B_DOUBLE_DISTRIBUTION = "b_double_distribution"
    TREND_DAY = "trend_day"
    NORMAL = "normal"
    UNDEFINED = "undefined"


class AtrQuantileConfig(BaseModel):
    """ATR 分位數配置（用於 ATR 指標）

    對應 Rust: AtrQuantileConfig struct

    用於計算 ATR 的滾動分位數，可用於動態止損等場景

    Example:
        >>> config = AtrQuantileConfig(window=20, quantile=0.5)  # 20 週期中位數
        >>> config = AtrQuantileConfig(window=20, quantile=0.75) # 20 週期 75% 分位數
    """

    window: int = Field(..., gt=0, description="滾動窗口大小（必須 > 0）")
    quantile: float = Field(
        ..., gt=0, lt=1, description="分位數值，範圍 (0, 1)，例如 0.5 表示中位數"
    )


class ProfileShapeConfig(BaseModel):
    """Profile 形狀識別配置（用於 MarketProfile 指標）

    對應 Rust: ProfileShapeConfig struct

    控制 Market Profile 形狀識別算法的閾值參數（進階功能，通常使用預設值即可）

    Profile 形狀類型：
    - "p_shaped": P型（快速上漲 + 高位盤整，看空信號）
    - "b_shaped": b型（快速下跌 + 低位盤整，看多信號）
    - "b_double_distribution": B型雙峰（區間交易）
    - "trend_day": 趨勢日（持續單向移動，順勢交易）
    - "normal": 正態分布（對稱分布，區間交易）
    - "undefined": 無法分類

    Example:
        >>> # 使用預設值（推薦）
        >>> config = ProfileShapeConfig()
        >>>
        >>> # 自訂閾值（進階）
        >>> config = ProfileShapeConfig(
        ...     trend_monotonic_threshold=0.65,
        ...     pshape_concentration_threshold=0.65
        ... )
    """

    early_period_ratio: float = Field(
        0.15, gt=0, le=1, description="早期時段比例（前 15% 視為早期）"
    )
    late_period_ratio: float = Field(
        0.15, gt=0, le=1, description="晚期時段比例（後 15% 視為晚期）"
    )
    trend_ib_max_ratio: float = Field(0.20, gt=0, le=1, description="趨勢日 IB 最大占比")
    trend_monotonic_threshold: float = Field(0.60, gt=0, le=1, description="趨勢日單向移動閾值")
    trend_imbalance_threshold: float = Field(
        0.70, gt=0, le=1, description="趨勢日早期/晚期 TPO 不平衡度閾值"
    )
    pshape_concentration_threshold: float = Field(
        0.60, gt=0, le=1, description="P型/b型 TPO 集中度閾值"
    )
    bshape_valley_threshold: float = Field(0.70, gt=0, le=1, description="B型雙峰之間谷的深度閾值")
    normal_symmetry_threshold: float = Field(0.30, gt=0, le=1, description="Normal 型對稱性閾值")


class MarketProfileIndicator(BaseModel):
    """Market Profile 指標

    對應 Rust: Indicator::MarketProfile { anchor_config, tick_size, value_area_pct, fields, shape_config }

    返回 Struct Series 包含以下欄位:
    - poc: Point of Control (f64)
    - vah: Value Area High (f64)
    - val: Value Area Low (f64)
    - value_area: VAH - VAL 範圍 (f64)
    - tpo_distribution: TPO 分布詳情 (List<Struct{price, count, periods}>)
    - segment_id: 時間區段 ID (u32，自動 ffill)
    - profile_shape: Profile 形狀類型 (String，需啟用 shape_config)

    Anchor 配置建議使用 helper functions:
    - create_daily_anchor(): 每日 Anchor（24 小時滾動窗口）
    - create_weekly_anchor(): 每週 Anchor（多日窗口）
    - create_initial_balance_anchor(): IB/RTH 窗口
    """

    type: Literal["MarketProfile"] = "MarketProfile"
    anchor_config: Dict[str, Any] = Field(
        ...,
        description="Anchor configuration (use create_daily_anchor, create_weekly_anchor, or create_initial_balance_anchor)",
    )
    tick_size: float = Field(gt=0, description="Tick size for price levels")
    value_area_pct: float = Field(default=0.7, gt=0, lt=1, description="Value area percentage")
    fields: Optional[List[str]] = Field(
        default=None,
        description="Select specific fields: ['poc', 'vah', 'val', 'value_area', 'tpo_distribution', 'profile_shape']",
    )
    shape_config: Optional[Dict[str, Any]] = Field(
        default=None, description="Profile shape recognition config (advanced feature)"
    )


# Helper functions for creating anchor configurations


def create_daily_anchor(
    hour: int,
    minute: int,
    lookback_days: int = 1,
) -> Dict[str, Any]:
    """創建每日 Anchor 配置（用於 Market Profile）

    Args:
        hour: 小時 (0-23)
        minute: 分鐘 (0-59)
        lookback_days: 回溯天數（預設 1）

    Returns:
        Anchor 配置 dict

    Note:
        系統固定使用 "ts" 和 "segment_id" 欄位名稱

    Example:
        >>> # 每日 09:15 結束，回溯 1 天
        >>> anchor = create_daily_anchor(9, 15, 1)
        >>> mp = Indicator.market_profile(
        ...     anchor_config=anchor,
        ...     tick_size=0.01
        ... )
    """
    return {
        "end_rule": {"type": "DailyTime", "hour": hour, "minute": minute},
        "start_rule": None,
        "lookback_days": lookback_days,
    }


def create_weekly_anchor(
    weekday: Union[int, str, Weekday],
    hour: int,
    minute: int,
    lookback_days: int = 5,
) -> Dict[str, Any]:
    """創建每週 Anchor 配置（用於 Market Profile）

    Args:
        weekday: 星期幾，支持多種格式:
            - int: 0=週一, 1=週二, ..., 6=週日
            - str: "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"
            - Weekday enum: Weekday.MON, Weekday.TUE, ...
        hour: 小時 (0-23)
        minute: 分鐘 (0-59)
        lookback_days: 回溯天數（預設 5）

    Returns:
        Anchor 配置 dict

    Note:
        系統固定使用 "ts" 和 "segment_id" 欄位名稱

    Example:
        >>> # 使用整數
        >>> anchor = create_weekly_anchor(0, 9, 15, 5)  # 週一
        >>> # 使用字串
        >>> anchor = create_weekly_anchor("Mon", 9, 15, 5)
        >>> # 使用 Weekday enum
        >>> anchor = create_weekly_anchor(Weekday.MON, 9, 15, 5)
        >>> mp = Indicator.market_profile(
        ...     anchor_config=anchor,
        ...     tick_size=0.01
        ... )
    """
    # 轉換 weekday 為字串格式
    weekday_map = {
        0: "Mon",
        1: "Tue",
        2: "Wed",
        3: "Thu",
        4: "Fri",
        5: "Sat",
        6: "Sun",
    }

    if isinstance(weekday, int):
        weekday_str = weekday_map[weekday]
    elif isinstance(weekday, Weekday):
        weekday_str = weekday.value
    else:
        weekday_str = str(weekday)

    return {
        "end_rule": {
            "type": "WeeklyTime",
            "weekday": weekday_str,
            "hour": hour,
            "minute": minute,
        },
        "start_rule": None,
        "lookback_days": lookback_days,
    }


def create_initial_balance_anchor(
    start_hour: int,
    start_minute: int,
    end_hour: int,
    end_minute: int,
) -> Dict[str, Any]:
    """創建 Initial Balance (IB) Anchor 配置（用於 Market Profile）

    Args:
        start_hour: 開始時間 - 小時 (0-23)
        start_minute: 開始時間 - 分鐘 (0-59)
        end_hour: 結束時間 - 小時 (0-23)
        end_minute: 結束時間 - 分鐘 (0-59)

    Returns:
        Anchor 配置 dict

    Note:
        - lookback_days 固定為 0（只計算當日時段內的數據）
        - 每天在 end_time 觸發一次計算
        - 適用於 IB (Initial Balance) 或 RTH (Regular Trading Hours) 分析

    Example:
        >>> # 每日 09:00-10:00 的 Initial Balance
        >>> anchor = create_initial_balance_anchor(9, 0, 10, 0)
        >>> mp = Indicator.market_profile(
        ...     anchor_config=anchor,
        ...     tick_size=0.01
        ... )
        >>>
        >>> # 美股 RTH (Regular Trading Hours): 09:30-16:00
        >>> anchor_rth = create_initial_balance_anchor(9, 30, 16, 0)
    """
    return {
        "start_rule": {"type": "DailyTime", "hour": start_hour, "minute": start_minute},
        "end_rule": {"type": "DailyTime", "hour": end_hour, "minute": end_minute},
        "lookback_days": 0,
    }


def create_profile_shape_config(
    early_period_ratio: float = 0.15,
    late_period_ratio: float = 0.15,
    trend_ib_max_ratio: float = 0.20,
    trend_monotonic_threshold: float = 0.60,
    trend_imbalance_threshold: float = 0.70,
    pshape_concentration_threshold: float = 0.60,
    bshape_valley_threshold: float = 0.70,
    normal_symmetry_threshold: float = 0.30,
) -> Dict[str, Any]:
    """創建 Profile 形狀識別配置（用於 MarketProfile 指標）

    Args:
        early_period_ratio: 早期時段比例（前 15% 視為早期），預設 0.15
        late_period_ratio: 晚期時段比例（後 15% 視為晚期），預設 0.15
        trend_ib_max_ratio: 趨勢日 IB 最大占比，預設 0.20
        trend_monotonic_threshold: 趨勢日單向移動閾值，預設 0.60
        trend_imbalance_threshold: 趨勢日早期/晚期 TPO 不平衡度閾值，預設 0.70
        pshape_concentration_threshold: P型/b型 TPO 集中度閾值，預設 0.60
        bshape_valley_threshold: B型雙峰之間谷的深度閾值，預設 0.70
        normal_symmetry_threshold: Normal 型對稱性閾值，預設 0.30

    Returns:
        Profile 形狀識別配置 dict

    Note:
        通常使用預設值即可，僅在需要微調形狀識別邏輯時才自訂參數

    Example:
        >>> # 使用預設值（推薦）
        >>> shape_config = create_profile_shape_config()
        >>> Indicator.market_profile(
        ...     anchor_config=create_daily_anchor(9, 15, 1),
        ...     tick_size=0.5,
        ...     shape_config=shape_config
        ... )
        >>>
        >>> # 自訂閾值（進階）
        >>> shape_config = create_profile_shape_config(
        ...     trend_monotonic_threshold=0.65,
        ...     pshape_concentration_threshold=0.65
        ... )
    """
    return {
        "early_period_ratio": early_period_ratio,
        "late_period_ratio": late_period_ratio,
        "trend_ib_max_ratio": trend_ib_max_ratio,
        "trend_monotonic_threshold": trend_monotonic_threshold,
        "trend_imbalance_threshold": trend_imbalance_threshold,
        "pshape_concentration_threshold": pshape_concentration_threshold,
        "bshape_valley_threshold": bshape_valley_threshold,
        "normal_symmetry_threshold": normal_symmetry_threshold,
    }
