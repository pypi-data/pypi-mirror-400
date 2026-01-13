"""
IndicatorSpec Model

Provides the IndicatorSpec class for specifying indicator configurations with frequency, shift, and instrument.
"""

from typing import Annotated, Any, Optional, Union

import polars as pl
from pydantic import BaseModel, Field, field_validator

from ..enums import Freq
from ..indicators import (
    ADXIndicator,
    ATRIndicator,
    ATRQuantileIndicator,
    BollingerBandsIndicator,
    CCIIndicator,
    EMAIndicator,
    MACDIndicator,
    MarketProfileIndicator,
    RawOhlcvIndicator,
    RSIIndicator,
    SMAIndicator,
    SMMAIndicator,
    StochasticIndicator,
    SuperTrendIndicator,
    WMAIndicator,
)

# ============================================================================
# Indicator Discriminated Union (强类型 Indicator 配置)
# ============================================================================

IndicatorConfig = Annotated[
    Union[
        # 移动平均类
        SMAIndicator,
        EMAIndicator,
        SMMAIndicator,
        WMAIndicator,
        # 波动率类
        ATRIndicator,
        ATRQuantileIndicator,
        # 趋势类
        SuperTrendIndicator,
        MACDIndicator,
        ADXIndicator,
        # 动量类
        RSIIndicator,
        CCIIndicator,
        StochasticIndicator,
        # 其他
        BollingerBandsIndicator,
        MarketProfileIndicator,
        RawOhlcvIndicator,
    ],
    Field(discriminator="type"),
]
"""
强类型 Indicator 配置

使用 Pydantic discriminated union，根据 'type' 字段自动选择正确的模型：
- type="SMA" → SMAIndicator
- type="ATR" → ATRIndicator
- type="SuperTrend" → SuperTrendIndicator
- ... etc

优点：
- 编译时类型检查
- IDE 自动补全
- 参数验证
- 自动 JSON 序列化/反序列化

Example:
    >>> # 方式 1: 直接创建强类型模型
    >>> atr = ATRIndicator(period=21)
    >>>
    >>> # 方式 2: 从 Dict 自动转换（API 兼容）
    >>> indicator: IndicatorConfig = {"type": "ATR", "period": 21}
    >>> # Pydantic 自动识别为 ATRIndicator
"""


class IndicatorSpec(BaseModel):
    """指標規範（强类型版本）"""

    instrument: Optional[str] = Field(
        None, description="交易標的（顯示名稱，可選，用於多商品場景）"
    )
    instrument_id: Optional[int] = Field(
        None, description="交易標的 ID（資料庫查詢用，由 Gateway 填充）"
    )
    freq: Freq = Field(..., description="頻率 (Freq enum)")
    shift: int = Field(1, description="位移（預設 1）")
    indicator: IndicatorConfig = Field(..., description="指標配置（强类型 Pydantic 模型）")

    @field_validator("freq", mode="before")
    @classmethod
    def convert_freq(cls, v: Any) -> Freq:
        """自動轉換字串為 Freq enum（保持 API 兼容性）"""
        if isinstance(v, str):
            try:
                return Freq(v)
            except ValueError:
                valid_values = [e.value for e in Freq]
                raise ValueError(f"Invalid freq: '{v}'. Valid values: {', '.join(valid_values)}")
        return v

    @field_validator("indicator", mode="before")
    @classmethod
    def convert_indicator(cls, v: Any) -> IndicatorConfig:
        """自動轉換 Dict 為強類型 Indicator 模型（保持 API 兼容性）

        接受：
        - Dict[str, Any]: 從 API 返回或舊代碼（自動轉換）
        - IndicatorConfig: 新代碼使用強類型模型

        Pydantic 會根據 'type' 字段自動選擇正確的模型。
        """
        # Dict 會被 Pydantic 自動轉換為對應的 Indicator 模型
        # 強類型模型直接返回
        return v

    @property
    def short_name(self) -> str:
        """生成指標簡短名稱（與 Rust 的 short_name 一致）

        格式範例:
        - SMA: "SMA|20.close"
        - EMA: "EMA|12.close"
        - ATR: "ATR|14"
        - SuperTrend: "ST|3.0x_atr"

        Returns:
            指標簡稱字符串

        Raises:
            ValueError: 未知的指標類型
        """
        indicator_type = self.indicator.type

        if indicator_type == "SMA":
            return f"SMA|{self.indicator.period}.{self.indicator.column}"

        elif indicator_type == "EMA":
            return f"EMA|{self.indicator.period}.{self.indicator.column}"

        elif indicator_type == "SMMA":
            return f"SMMA|{self.indicator.period}.{self.indicator.column}"

        elif indicator_type == "WMA":
            return f"WMA|{self.indicator.period}.{self.indicator.column}"

        elif indicator_type == "ATR":
            # ATR 始終返回單一數值欄位，無 quantile
            return f"ATR|{self.indicator.period}"

        elif indicator_type == "AtrQuantile":
            # 將 quantile 轉為百分比（例如 0.5 -> 50）
            quantile_pct = int(self.indicator.quantile * 100)
            # 格式：ATRQ|{atr_column}_Q{quantile%}_{window}
            return f"ATRQ|{self.indicator.atr_column}_Q{quantile_pct}_{self.indicator.window}"

        elif indicator_type == "SuperTrend":
            return f"ST|{self.indicator.multiplier}x_{self.indicator.volatility_column}"

        elif indicator_type == "MarketProfile":
            # 提取 anchor_config 資訊
            anchor_config = self.indicator.anchor_config
            end_rule = anchor_config.get("end_rule", {})
            lookback_days = anchor_config.get("lookback_days", 1)
            tick_size = self.indicator.tick_size

            # 格式化時間字串（支持新舊兩種格式）
            rule_type = end_rule.get("type")

            if rule_type == "DailyTime" or "DailyTime" in end_rule:
                # 新格式: {"type": "DailyTime", "hour": 9, "minute": 15}
                # 舊格式: {"DailyTime": {"hour": 9, "minute": 15}}
                if rule_type == "DailyTime":
                    time_str = f"{end_rule['hour']:02d}{end_rule['minute']:02d}"
                else:
                    daily = end_rule["DailyTime"]
                    time_str = f"{daily['hour']:02d}{daily['minute']:02d}"

            elif rule_type == "WeeklyTime" or "WeeklyTime" in end_rule:
                # 新格式: {"type": "WeeklyTime", "weekday": "Mon", "hour": 9, "minute": 15}
                # 舊格式: {"WeeklyTime": {"weekday": 0, "hour": 9, "minute": 15}}
                # 輸出格式: W{weekday_int}{HHMM} (與 Rust Server 一致)
                str_to_int_map = {
                    "Mon": 0,
                    "Tue": 1,
                    "Wed": 2,
                    "Thu": 3,
                    "Fri": 4,
                    "Sat": 5,
                    "Sun": 6,
                }
                if rule_type == "WeeklyTime":
                    weekday = end_rule["weekday"]
                    # weekday 可能是字串 ("Mon") 或整數 (0)
                    if isinstance(weekday, str):
                        weekday_int = str_to_int_map.get(weekday, 0)
                    else:
                        weekday_int = weekday
                    time_str = f"W{weekday_int}{end_rule['hour']:02d}{end_rule['minute']:02d}"
                else:
                    weekly = end_rule["WeeklyTime"]
                    weekday = weekly["weekday"]
                    if isinstance(weekday, str):
                        weekday_int = str_to_int_map.get(weekday, 0)
                    else:
                        weekday_int = weekday
                    time_str = f"W{weekday_int}{weekly['hour']:02d}{weekly['minute']:02d}"
            else:
                time_str = "UNKNOWN"

            # 格式: MP|{time}_{lookback_days}_{tick_size}
            # 注意：MarketProfile 不支持 indicator 層級的 shift
            # TODO: 臨時方案 - 整數顯示為整數，非整數保留小數（與 Rust 行為一致）
            #       詳見 docs/issues/tick-size-float-formatting-mismatch.md
            tick_str = str(int(tick_size)) if tick_size == int(tick_size) else str(tick_size)
            return f"MP|{time_str}_{lookback_days}_{tick_str}"

        elif indicator_type == "CCI":
            return f"CCI|{self.indicator.period}"

        elif indicator_type == "RSI":
            return f"RSI|{self.indicator.period}"

        elif indicator_type == "BollingerBands":
            return f"BB|{self.indicator.period}_{self.indicator.num_std}"

        elif indicator_type == "MACD":
            return f"MACD|{self.indicator.fast_period}_{self.indicator.slow_period}_{self.indicator.signal_period}"

        elif indicator_type == "Stochastic":
            return f"STOCH|{self.indicator.k_period}_{self.indicator.d_period}"

        elif indicator_type == "ADX":
            return f"ADX|{self.indicator.period}"

        elif indicator_type == "RawOhlcv":
            # RawOhlcv 只返回 column 名稱
            return self.indicator.column

        else:
            raise ValueError(f"未知的指標類型: {indicator_type}")

    @property
    def display_name(self) -> str:
        """生成完整的 column 名稱（與 Rust 的 display_name 一致）

        格式:
        - 有 instrument_id: "{instrument_id}_{freq}_{indicator_short_name}[_s{shift}]"
        - 無 instrument_id: "{freq}_{indicator_short_name}[_s{shift}]"

        範例:
        - "ES_1min_SMA|20.close"      (shift=1，不顯示)
        - "1D_ATR|14_s2"               (shift=2)
        - "BTC_5min_EMA|12.close_s2"  (shift=2)
        - "1h_ST|3.0x_atr"            (無 instrument_id)

        Returns:
            完整的 column 名稱字符串
        """
        parts = []

        # 1. instrument（如果有）
        if self.instrument:
            parts.append(self.instrument)

        # 2. freq（處理 Freq enum）
        freq_str = self.freq.value if isinstance(self.freq, Freq) else self.freq
        parts.append(freq_str)

        # 3. indicator short name
        parts.append(self.short_name)

        # 4. shift（只在非預設值時加入）
        if self.shift != 1:
            parts.append(f"s{self.shift}")

        return "_".join(parts)

    def col(self) -> pl.Expr:
        """返回 Polars column expression（最常用的便捷方法）

        Returns:
            pl.col(display_name) 的 Polars 表達式

        Example:
            >>> spec = IndicatorSpec(
            ...     instrument_id="ES",
            ...     freq="1min",
            ...     shift=1,
            ...     indicator={"type": "SMA", "period": 20, "column": "close"}
            ... )
            >>> # 直接在條件中使用
            >>> condition = spec.col() > 100
            >>> # 或在過濾中使用
            >>> df.filter(spec.col() > pl.col("open"))
        """
        return pl.col(self.display_name)

    # ========================================================================
    # Struct Field Accessors
    # ========================================================================

    @property
    def market_profile(self) -> "MarketProfileAccessor":
        """MarketProfile struct 欄位存取器"""
        return MarketProfileAccessor(self)

    @property
    def supertrend(self) -> "SuperTrendAccessor":
        """SuperTrend struct 欄位存取器"""
        return SuperTrendAccessor(self)

    @property
    def macd_fields(self) -> "MACDAccessor":
        """MACD struct 欄位存取器"""
        return MACDAccessor(self)

    @property
    def adx_fields(self) -> "ADXAccessor":
        """ADX struct 欄位存取器"""
        return ADXAccessor(self)

    @property
    def stochastic(self) -> "StochasticAccessor":
        """Stochastic struct 欄位存取器"""
        return StochasticAccessor(self)

    @property
    def bollinger_bands(self) -> "BollingerBandsAccessor":
        """BollingerBands struct 欄位存取器"""
        return BollingerBandsAccessor(self)


# ============================================================================
# Struct Field Accessors
# ============================================================================


class StructFieldAccessor:
    """Struct 欄位存取器基類"""

    def __init__(self, spec: IndicatorSpec):
        self._spec = spec

    @property
    def struct_col(self) -> pl.Expr:
        """返回整個 struct 的 Polars 表達式"""
        return self._spec.col()

    def _field(self, name: str) -> pl.Expr:
        """內部方法：取得 struct 子欄位"""
        return self.struct_col.struct.field(name)


class MarketProfileAccessor(StructFieldAccessor):
    """MarketProfile struct 欄位存取器

    Example:
        >>> mp = IndicatorSpec(freq=Freq.MIN_30, indicator=MarketProfileIndicator(...))
        >>> mp.market_profile.poc           # pl.col(...).struct.field("poc")
        >>> mp.market_profile.vah           # pl.col(...).struct.field("vah")
        >>> mp.market_profile.profile_shape # pl.col(...).struct.field("profile_shape")
    """

    @property
    def poc(self) -> pl.Expr:
        """Point of Control"""
        return self._field("poc")

    @property
    def vah(self) -> pl.Expr:
        """Value Area High"""
        return self._field("vah")

    @property
    def val(self) -> pl.Expr:
        """Value Area Low"""
        return self._field("val")

    @property
    def value_area(self) -> pl.Expr:
        """Value Area (VAH - VAL)"""
        return self._field("value_area")

    @property
    def segment_id(self) -> pl.Expr:
        """Segment ID"""
        return self._field("segment_id")

    @property
    def profile_shape(self) -> pl.Expr:
        """Profile Shape (p_shape, b_shape, trend_day, normal, etc.)"""
        return self._field("profile_shape")

    @property
    def tpo_distribution(self) -> pl.Expr:
        """TPO Distribution"""
        return self._field("tpo_distribution")


class SuperTrendAccessor(StructFieldAccessor):
    """SuperTrend struct 欄位存取器

    Example:
        >>> st = IndicatorSpec(freq=Freq.MIN_30, indicator=SuperTrendIndicator(...))
        >>> st.supertrend.direction   # pl.col(...).struct.field("direction")
        >>> st.supertrend.supertrend  # pl.col(...).struct.field("supertrend")
    """

    @property
    def direction(self) -> pl.Expr:
        """Trend direction (1 = up, -1 = down)"""
        return self._field("direction")

    @property
    def supertrend(self) -> pl.Expr:
        """SuperTrend value"""
        return self._field("supertrend")

    @property
    def long(self) -> pl.Expr:
        """Long stop level"""
        return self._field("long")

    @property
    def short(self) -> pl.Expr:
        """Short stop level"""
        return self._field("short")


class MACDAccessor(StructFieldAccessor):
    """MACD struct 欄位存取器

    Example:
        >>> macd = IndicatorSpec(freq=Freq.MIN_30, indicator=MACDIndicator(...))
        >>> macd.macd_fields.macd      # pl.col(...).struct.field("macd")
        >>> macd.macd_fields.histogram # pl.col(...).struct.field("histogram")
    """

    @property
    def macd(self) -> pl.Expr:
        """MACD line"""
        return self._field("macd")

    @property
    def signal(self) -> pl.Expr:
        """Signal line"""
        return self._field("signal")

    @property
    def histogram(self) -> pl.Expr:
        """MACD histogram"""
        return self._field("histogram")


class ADXAccessor(StructFieldAccessor):
    """ADX struct 欄位存取器

    Example:
        >>> adx = IndicatorSpec(freq=Freq.MIN_30, indicator=ADXIndicator(...))
        >>> adx.adx_fields.adx      # pl.col(...).struct.field("adx")
        >>> adx.adx_fields.plus_di  # pl.col(...).struct.field("plus_di")
    """

    @property
    def adx(self) -> pl.Expr:
        """ADX value"""
        return self._field("adx")

    @property
    def plus_di(self) -> pl.Expr:
        """+DI value"""
        return self._field("plus_di")

    @property
    def minus_di(self) -> pl.Expr:
        """-DI value"""
        return self._field("minus_di")


class StochasticAccessor(StructFieldAccessor):
    """Stochastic struct 欄位存取器

    Example:
        >>> stoch = IndicatorSpec(freq=Freq.MIN_30, indicator=StochasticIndicator(...))
        >>> stoch.stochastic.k  # pl.col(...).struct.field("k")
        >>> stoch.stochastic.d  # pl.col(...).struct.field("d")
    """

    @property
    def k(self) -> pl.Expr:
        """%K value"""
        return self._field("k")

    @property
    def d(self) -> pl.Expr:
        """%D value"""
        return self._field("d")


class BollingerBandsAccessor(StructFieldAccessor):
    """BollingerBands struct 欄位存取器

    Example:
        >>> bb = IndicatorSpec(freq=Freq.MIN_30, indicator=BollingerBandsIndicator(...))
        >>> bb.bollinger_bands.upper  # pl.col(...).struct.field("upper")
        >>> bb.bollinger_bands.lower  # pl.col(...).struct.field("lower")
    """

    @property
    def upper(self) -> pl.Expr:
        """Upper band"""
        return self._field("upper")

    @property
    def middle(self) -> pl.Expr:
        """Middle band (SMA)"""
        return self._field("middle")

    @property
    def lower(self) -> pl.Expr:
        """Lower band"""
        return self._field("lower")
