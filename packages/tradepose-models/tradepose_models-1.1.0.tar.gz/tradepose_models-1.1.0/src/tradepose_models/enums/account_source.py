"""AccountSource enumeration for brokers and prop firms."""

from datetime import datetime
from enum import StrEnum
from zoneinfo import ZoneInfo


class AccountSource(StrEnum):
    """帳戶來源 / Broker / Prop firm"""

    FTMO = "FTMO"
    IB = "IB"
    FIVEPERCENT = "FIVEPERCENT"
    BINANCE = "BINANCE"
    SHIOAJI = "SHIOAJI"

    def timezone(self) -> str:
        """Returns IANA timezone string for this account source.

        Returns:
            IANA timezone string (e.g., "Europe/Athens", "America/New_York")
        """
        timezones = {
            AccountSource.FTMO: "Europe/Athens",
            AccountSource.IB: "America/New_York",
            AccountSource.FIVEPERCENT: "Europe/Moscow",
            AccountSource.BINANCE: "Etc/UTC",
            AccountSource.SHIOAJI: "Asia/Taipei",
        }
        return timezones.get(self, "Etc/UTC")

    def tz_offset(self) -> int:
        """動態計算當前 UTC 偏移（考慮 DST）

        Returns:
            Current UTC offset in hours (DST-aware)
        """
        tz = ZoneInfo(self.timezone())
        offset = datetime.now(tz).utcoffset()
        if offset is None:
            return 0
        return int(offset.total_seconds() / 3600)
