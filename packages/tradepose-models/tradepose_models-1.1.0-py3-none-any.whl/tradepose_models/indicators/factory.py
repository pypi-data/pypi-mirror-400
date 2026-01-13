"""
Indicator Factory Class

Provides static methods to create indicator configurations with a Rust-like API.
"""

from typing import Any, Dict, List, Optional

from .market_profile import MarketProfileIndicator
from .momentum import CCIIndicator, RSIIndicator, StochasticIndicator
from .moving_average import EMAIndicator, SMAIndicator, SMMAIndicator, WMAIndicator
from .other import BollingerBandsIndicator, RawOhlcvIndicator
from .trend import ADXIndicator, MACDIndicator, SuperTrendIndicator
from .volatility import ATRIndicator, ATRQuantileIndicator


class Indicator:
    """指標工廠類（對應 Rust 的 Indicator enum）

    使用靜態方法創建各種指標配置，語法類似 Rust 的關聯函數

    支援的指標類型（15 種）：
    - 移動平均: SMA, EMA, SMMA, WMA
    - 波動率: ATR, AtrQuantile
    - 通道指標: BollingerBands
    - 趨勢指標: SuperTrend, ADX, MACD
    - 動量指標: RSI, CCI, Stochastic
    - 價格分布: MarketProfile
    - 原始數據: RawOhlcv

    Example:
        >>> from tradepose_models import Indicator
        >>>
        >>> # 移動平均
        >>> sma = Indicator.sma(period=20)
        >>> sma_on_high = Indicator.sma(period=20, column="high")
        >>> ema = Indicator.ema(period=12)
        >>>
        >>> # 波動率
        >>> atr = Indicator.atr(period=14)
        >>> atr_q = Indicator.atr_quantile("ATR|14", window=20, quantile=0.75)
        >>>
        >>> # 通道指標
        >>> bb = Indicator.bollinger_bands(period=20, num_std=2.0)
        >>>
        >>> # 趨勢指標
        >>> st = Indicator.supertrend(multiplier=3.0, volatility_column="ATR|14")
        >>> macd = Indicator.macd(fast_period=12, slow_period=26, signal_period=9)
        >>> adx = Indicator.adx(period=14)
        >>>
        >>> # 動量指標
        >>> rsi = Indicator.rsi(period=14)
        >>> cci = Indicator.cci(period=20)
        >>> stoch = Indicator.stochastic(k_period=14, d_period=3)
    """

    @staticmethod
    def sma(period: int, column: str = "close") -> SMAIndicator:
        """創建 SMA 指標配置（强类型）

        對應 Rust: Indicator::SMA { period, column }

        Args:
            period: 週期
            column: 計算欄位（預設 "close"）

        Returns:
            SMAIndicator 強類型模型

        Example:
            >>> sma = Indicator.sma(period=20)
            >>> assert isinstance(sma, SMAIndicator)
            >>> sma_high = Indicator.sma(period=20, column="high")
        """
        return SMAIndicator(period=period, column=column)

    @staticmethod
    def ema(period: int, column: str = "close") -> EMAIndicator:
        """創建 EMA 指標配置（强类型）

        對應 Rust: Indicator::EMA { period, column }
        """
        return EMAIndicator(period=period, column=column)

    @staticmethod
    def smma(period: int, column: str = "close") -> SMMAIndicator:
        """創建 SMMA 指標配置（强类型）

        對應 Rust: Indicator::SMMA { period, column }
        """
        return SMMAIndicator(period=period, column=column)

    @staticmethod
    def wma(period: int, column: str = "close") -> WMAIndicator:
        """創建 WMA 指標配置（强类型）

        對應 Rust: Indicator::WMA { period, column }
        """
        return WMAIndicator(period=period, column=column)

    @staticmethod
    def atr(period: int) -> ATRIndicator:
        """創建 ATR 指標配置（强类型）

        對應 Rust: Indicator::ATR { period }
        """
        return ATRIndicator(period=period)

    @staticmethod
    def atr_quantile(
        atr_column: str,
        window: int,
        quantile: float,
    ) -> ATRQuantileIndicator:
        """創建 AtrQuantile 指標配置（强类型）

        對應 Rust: Indicator::AtrQuantile { atr_column, window, quantile }
        """
        return ATRQuantileIndicator(
            atr_column=atr_column,
            window=window,
            quantile=quantile,
        )

    @staticmethod
    def supertrend(
        multiplier: float,
        volatility_column: str,
        high: str = "high",
        low: str = "low",
        close: str = "close",
        fields: Optional[List[str]] = None,
    ) -> SuperTrendIndicator:
        """創建 SuperTrend 指標配置（强类型）

        對應 Rust: Indicator::SuperTrend { multiplier, volatility_column, high, low, close, fields }
        """
        return SuperTrendIndicator(
            multiplier=float(multiplier),
            volatility_column=volatility_column,
            high=high,
            low=low,
            close=close,
            fields=fields,
        )

    @staticmethod
    def market_profile(
        anchor_config: Dict[str, Any],
        tick_size: float,
        value_area_pct: float = 0.7,
        fields: Optional[List[str]] = None,
        shape_config: Optional[Dict[str, Any]] = None,
    ) -> MarketProfileIndicator:
        """創建 Market Profile 指標配置（强类型）

        對應 Rust: Indicator::MarketProfile { anchor_config, tick_size, ... }
        """
        return MarketProfileIndicator(
            anchor_config=anchor_config,
            tick_size=tick_size,
            value_area_pct=value_area_pct,
            fields=fields,
            shape_config=shape_config,
        )

    @staticmethod
    def cci(period: int = 20) -> CCIIndicator:
        """創建 CCI 指標配置（强类型）

        對應 Rust: Indicator::CCI { period }
        """
        return CCIIndicator(period=period)

    @staticmethod
    def rsi(period: int = 14, column: str = "close") -> RSIIndicator:
        """創建 RSI 指標配置（强类型）

        對應 Rust: Indicator::RSI { period, column }
        """
        return RSIIndicator(period=period, column=column)

    @staticmethod
    def bollinger_bands(
        period: int = 20,
        num_std: float = 2.0,
        column: str = "close",
        fields: Optional[List[str]] = None,
    ) -> BollingerBandsIndicator:
        """創建 Bollinger Bands 指標配置（强类型）

        對應 Rust: Indicator::BollingerBands { period, num_std, column, fields }
        """
        return BollingerBandsIndicator(
            period=period,
            num_std=float(num_std),
            column=column,
            fields=fields,
        )

    @staticmethod
    def macd(
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        column: str = "close",
        fields: Optional[List[str]] = None,
    ) -> MACDIndicator:
        """創建 MACD 指標配置（强类型）

        對應 Rust: Indicator::MACD { fast_period, slow_period, signal_period, column, fields }
        """
        return MACDIndicator(
            fast_period=fast_period,
            slow_period=slow_period,
            signal_period=signal_period,
            column=column,
            fields=fields,
        )

    @staticmethod
    def stochastic(
        k_period: int = 14,
        d_period: int = 3,
        fields: Optional[List[str]] = None,
    ) -> StochasticIndicator:
        """創建 Stochastic 指標配置（强类型）

        對應 Rust: Indicator::Stochastic { k_period, d_period, fields }
        """
        return StochasticIndicator(
            k_period=k_period,
            d_period=d_period,
            fields=fields,
        )

    @staticmethod
    def adx(period: int = 14, fields: Optional[List[str]] = None) -> ADXIndicator:
        """創建 ADX 指標配置（强类型）

        對應 Rust: Indicator::ADX { period, fields }
        """
        return ADXIndicator(
            period=period,
            fields=fields,
        )

    @staticmethod
    def raw_ohlcv(column: str) -> RawOhlcvIndicator:
        """創建 RawOhlcv 指標配置（强类型）

        對應 Rust: Indicator::RawOhlcv { column }
        """
        return RawOhlcvIndicator(column=column)
