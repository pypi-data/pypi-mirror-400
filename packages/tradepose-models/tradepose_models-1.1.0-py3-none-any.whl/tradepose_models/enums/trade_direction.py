"""Trade direction enumeration."""

from enum import Enum


class TradeDirection(str, Enum):
    """Trade direction enum.

    Used to specify the trading direction in Blueprint.
    String values match Rust's TradeDirection enum.

    Values:
        LONG: Long trades only (multiplier: 1)
        SHORT: Short trades only (multiplier: -1)
        BOTH: Both long and short trades (currently not fully supported)
    """

    LONG = "Long"
    SHORT = "Short"
    BOTH = "Both"

    def to_int(self) -> int:
        """Convert to integer multiplier (1=Long, -1=Short).

        Matches Rust's direction_multiplier() function.
        """
        if self == TradeDirection.LONG:
            return 1
        elif self == TradeDirection.SHORT:
            return -1
        else:
            raise ValueError(f"Cannot convert {self} to int multiplier")

    @classmethod
    def from_int(cls, value: int) -> "TradeDirection":
        """Create from integer multiplier (1=Long, -1=Short)."""
        if value == 1:
            return cls.LONG
        elif value == -1:
            return cls.SHORT
        else:
            raise ValueError(f"Invalid direction int: {value}. Expected 1 or -1.")
