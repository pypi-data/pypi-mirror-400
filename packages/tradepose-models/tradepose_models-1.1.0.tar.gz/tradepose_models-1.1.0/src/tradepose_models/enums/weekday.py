"""
Weekday enumeration
"""

from enum import Enum


class Weekday(str, Enum):
    """
    Weekday enum (aligned with Rust Weekday enum)

    Used for Market Profile WeeklyTime configuration.

    Mapping:
        MON (Monday) = 0
        TUE (Tuesday) = 1
        WED (Wednesday) = 2
        THU (Thursday) = 3
        FRI (Friday) = 4
        SAT (Saturday) = 5
        SUN (Sunday) = 6
    """

    MON = "Mon"
    TUE = "Tue"
    WED = "Wed"
    THU = "Thu"
    FRI = "Fri"
    SAT = "Sat"
    SUN = "Sun"
