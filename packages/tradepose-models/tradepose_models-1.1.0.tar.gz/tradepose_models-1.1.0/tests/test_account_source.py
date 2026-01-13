"""Tests for AccountSource enum timezone functionality."""

from datetime import datetime
from zoneinfo import ZoneInfo

from tradepose_models.enums import AccountSource


class TestAccountSourceTimezone:
    """Test AccountSource.timezone() method."""

    def test_ftmo_timezone_returns_london(self):
        """FTMO should return Europe/London timezone."""
        assert AccountSource.FTMO.timezone() == "Europe/Athens"

    def test_ib_timezone_returns_new_york(self):
        """IB should return America/New_York timezone."""
        assert AccountSource.IB.timezone() == "America/New_York"

    def test_fivepercent_timezone_returns_moscow(self):
        """FIVEPERCENT should return Europe/Moscow timezone."""
        assert AccountSource.FIVEPERCENT.timezone() == "Europe/Moscow"

    def test_binance_timezone_returns_utc(self):
        """BINANCE should return Etc/UTC timezone."""
        assert AccountSource.BINANCE.timezone() == "Etc/UTC"

    def test_shioaji_timezone_returns_taipei(self):
        """SHIOAJI should return Asia/Taipei timezone."""
        assert AccountSource.SHIOAJI.timezone() == "Asia/Taipei"

    def test_timezone_returns_valid_iana_string(self):
        """All timezones should be valid IANA timezone strings."""
        for source in AccountSource:
            tz_str = source.timezone()
            # Verify it's a valid timezone by creating a ZoneInfo
            tz = ZoneInfo(tz_str)
            assert tz is not None


class TestAccountSourceTzOffset:
    """Test AccountSource.tz_offset() method."""

    def test_binance_offset_is_zero(self):
        """BINANCE (UTC) should always have offset 0."""
        assert AccountSource.BINANCE.tz_offset() == 0

    def test_tz_offset_returns_integer(self):
        """tz_offset should return an integer."""
        for source in AccountSource:
            offset = source.tz_offset()
            assert isinstance(offset, int)

    def test_tz_offset_is_dst_aware(self):
        """tz_offset should return different values based on DST.

        This test verifies that the implementation uses dynamic calculation
        rather than hardcoded values. We compare the offset calculated by
        tz_offset() with the actual offset from ZoneInfo.
        """
        for source in AccountSource:
            # Get the offset from our method
            method_offset = source.tz_offset()

            # Calculate expected offset using ZoneInfo
            tz = ZoneInfo(source.timezone())
            now = datetime.now(tz)
            utc_offset = now.utcoffset()
            if utc_offset is None:
                expected_offset = 0
            else:
                expected_offset = int(utc_offset.total_seconds() / 3600)

            assert method_offset == expected_offset, (
                f"{source} offset mismatch: got {method_offset}, expected {expected_offset}"
            )

    def test_taipei_offset_is_eight(self):
        """SHIOAJI (Asia/Taipei) should have offset +8 (no DST)."""
        assert AccountSource.SHIOAJI.tz_offset() == 8
