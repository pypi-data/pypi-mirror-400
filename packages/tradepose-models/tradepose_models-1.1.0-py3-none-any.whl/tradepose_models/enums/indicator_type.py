"""
Indicator type enumeration
"""

from enum import Enum


class IndicatorType(str, Enum):
    """
    Indicator type enum

    Maps to Indicator factory methods in models.py.

    Values:
        SMA: Simple Moving Average
        EMA: Exponential Moving Average
        SMMA: Smoothed Moving Average
        WMA: Weighted Moving Average
        ATR: Average True Range
        ATR_QUANTILE: ATR Rolling Quantile
        SUPERTREND: SuperTrend
        MARKET_PROFILE: Market Profile
        CCI: Commodity Channel Index
        RSI: Relative Strength Index
        BOLLINGER_BANDS: Bollinger Bands
        MACD: Moving Average Convergence Divergence
        STOCHASTIC: Stochastic Oscillator
        ADX: Average Directional Index
        RAW_OHLCV: Raw OHLCV column
    """

    SMA = "sma"
    EMA = "ema"
    SMMA = "smma"
    WMA = "wma"
    ATR = "atr"
    ATR_QUANTILE = "atr_quantile"
    SUPERTREND = "supertrend"
    MARKET_PROFILE = "market_profile"
    CCI = "cci"
    RSI = "rsi"
    BOLLINGER_BANDS = "bollinger_bands"
    MACD = "macd"
    STOCHASTIC = "stochastic"
    ADX = "adx"
    RAW_OHLCV = "raw_ohlcv"
