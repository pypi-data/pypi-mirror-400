"""
Time frequency enumeration
"""

from enum import Enum


class Freq(str, Enum):
    """
    Time frequency enum (aligned with Rust Freq enum)

    Values:
        MIN_1: 1 minute
        MIN_5: 5 minutes
        MIN_15: 15 minutes
        MIN_30: 30 minutes
        HOUR_1: 1 hour
        HOUR_4: 4 hours
        DAY_1: 1 day
        WEEK_1: 1 week
        MONTH_1: 1 month
    """

    MIN_1 = "1min"
    MIN_5 = "5min"
    MIN_15 = "15min"
    MIN_30 = "30min"
    HOUR_1 = "1h"
    HOUR_4 = "4h"
    DAY_1 = "1D"
    WEEK_1 = "1W"
    MONTH_1 = "1M"
