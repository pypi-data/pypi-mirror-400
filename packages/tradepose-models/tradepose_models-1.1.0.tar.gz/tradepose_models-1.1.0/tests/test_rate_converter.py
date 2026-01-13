"""Tests for the RateConverter module."""

from decimal import Decimal

import pytest
from tradepose_models.enums import Currency
from tradepose_models.utils.rate_converter import (
    DEFAULT_RATES,
    RateConverter,
    get_default_converter,
)


@pytest.fixture
def converter() -> RateConverter:
    """Create a test converter with simplified rates."""
    rates = {
        Currency.USD: Decimal("1"),
        Currency.TWD: Decimal("1") / Decimal("32.5"),
        Currency.BTC: Decimal("95000"),
        Currency.ETH: Decimal("3400"),
        Currency.EUR: Decimal("1.08"),
        Currency.USDT: Decimal("1"),
    }
    return RateConverter(rates)


# TC-001: Basic conversion
def test_basic_conversion(converter: RateConverter) -> None:
    """Test basic USD to TWD conversion."""
    result = converter.convert(Decimal("1000"), Currency.USD, Currency.TWD)
    assert result == Decimal("32500")


# TC-002: Roundtrip consistency
def test_roundtrip_consistency(converter: RateConverter) -> None:
    """Test that converting back and forth returns the original amount."""
    original = Decimal("1000")
    twd = converter.convert(original, Currency.USD, Currency.TWD)
    back = converter.convert(twd, Currency.TWD, Currency.USD)
    assert abs(back - original) < Decimal("1e-10")


# TC-003: Same currency conversion
def test_same_currency(converter: RateConverter) -> None:
    """Test that converting to the same currency returns the same amount."""
    assert converter.convert(Decimal("100"), Currency.USD, Currency.USD) == Decimal("100")


# TC-004: Zero amount
def test_zero_amount(converter: RateConverter) -> None:
    """Test that zero amount converts to zero."""
    assert converter.convert(Decimal("0"), Currency.USD, Currency.TWD) == Decimal("0")


# TC-005: Invalid currency
def test_invalid_currency(converter: RateConverter) -> None:
    """Test that unsupported currency raises ValueError."""
    with pytest.raises(ValueError, match="不支援的幣種"):
        converter.convert(Decimal("100"), Currency.USD, Currency.XAU)


# TC-006: Crypto conversion
def test_crypto_conversion(converter: RateConverter) -> None:
    """Test ETH to BTC conversion."""
    # 2.5 ETH → BTC
    # 2.5 × 3400 = 8500 USD
    # 8500 / 95000 ≈ 0.0895 BTC
    result = converter.convert(Decimal("2.5"), Currency.ETH, Currency.BTC)
    expected = Decimal("8500") / Decimal("95000")
    assert abs(result - expected) < Decimal("0.0001")


# TC-007: Large number precision
def test_large_number_precision(converter: RateConverter) -> None:
    """Test precision with large numbers."""
    result = converter.convert(Decimal("1e10"), Currency.USD, Currency.TWD)
    assert result == Decimal("3.25e11")


# TC-008: Negative amount (for P&L calculations)
def test_negative_amount(converter: RateConverter) -> None:
    """Test that negative amounts are handled correctly."""
    result = converter.convert(Decimal("-100"), Currency.USD, Currency.TWD)
    assert result == Decimal("-3250")


# TC-009: USD base validation
def test_usd_base_validation() -> None:
    """Test that USD rate must be 1."""
    with pytest.raises(ValueError, match="USD 必須為基準貨幣"):
        RateConverter({Currency.USD: Decimal("2")})


# TC-010: Positive rate validation
def test_positive_rate_validation() -> None:
    """Test that all rates must be positive."""
    with pytest.raises(ValueError, match="所有匯率必須為正數"):
        RateConverter({Currency.USD: Decimal("1"), Currency.TWD: Decimal("-0.03")})


# TC-011: Default rates completeness
def test_default_rates_completeness() -> None:
    """Ensure DEFAULT_RATES contains all Currency enum values."""
    for currency in Currency:
        assert currency in DEFAULT_RATES, f"DEFAULT_RATES 缺少 {currency}"


# TC-012: get_default_converter factory function
def test_get_default_converter() -> None:
    """Test that get_default_converter returns a working converter."""
    converter = get_default_converter()
    # Verify conversion works
    result = converter.convert(Decimal("1"), Currency.USD, Currency.TWD)
    assert result > 0


# TC-013: get_rate method
def test_get_rate(converter: RateConverter) -> None:
    """Test the get_rate method."""
    rate = converter.get_rate(Currency.USD, Currency.TWD)
    # 1 USD should give 32.5 TWD
    assert rate == Decimal("32.5")


# TC-014: get_rate with invalid currency
def test_get_rate_invalid_currency(converter: RateConverter) -> None:
    """Test get_rate with unsupported currency."""
    with pytest.raises(ValueError, match="不支援的幣種"):
        converter.get_rate(Currency.USD, Currency.XAU)
