"""
Trend type enumeration
"""

from enum import Enum


class TrendType(str, Enum):
    """
    Trend type enum

    Used to categorize strategy trading style.

    Values:
        TREND: Trend-following strategies
        RANGE: Range-bound/mean-reversion strategies
        REVERSAL: Reversal/counter-trend strategies
    """

    TREND = "Trend"
    RANGE = "Range"
    REVERSAL = "Reversal"
