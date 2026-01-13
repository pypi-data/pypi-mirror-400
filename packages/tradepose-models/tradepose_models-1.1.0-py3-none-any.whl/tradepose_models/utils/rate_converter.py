"""Multi-currency rate converter module.

Provides currency conversion utilities with USD as the base currency.
All conversions A → B are executed as A → USD → B.
"""

from decimal import Decimal

from tradepose_models.enums import Currency

# Default exchange rates (1 unit of currency = X USD)
DEFAULT_RATES: dict[Currency, Decimal] = {
    # Base currencies
    Currency.USD: Decimal("1"),
    Currency.USDT: Decimal("1"),
    # Fiat currencies
    Currency.TWD: Decimal("1") / Decimal("32.5"),  # 1 TWD ≈ 0.0308 USD
    Currency.EUR: Decimal("1.08"),  # 1 EUR = 1.08 USD
    Currency.JPY: Decimal("1") / Decimal("157"),  # 1 JPY ≈ 0.0064 USD
    # Cryptocurrencies
    Currency.BTC: Decimal("95000"),  # 1 BTC = 95000 USD
    Currency.ETH: Decimal("3400"),  # 1 ETH = 3400 USD
    # Commodities/Indices
    Currency.XAU: Decimal("2600"),  # 1 oz Gold = 2600 USD
    Currency.TAIEX: Decimal("200") / Decimal("32.5"),  # TAIEX point value: 200 TWD
}


class RateConverter:
    """Multi-currency rate converter.

    Uses USD as the base currency for a centralized conversion model.
    All conversions A → B are executed as A → USD → B.

    Example:
        >>> rates = {Currency.USD: Decimal("1"), Currency.TWD: Decimal("0.0308")}
        >>> converter = RateConverter(rates)
        >>> converter.convert(Decimal("1000"), Currency.USD, Currency.TWD)
        Decimal('32467.532467...')
    """

    def __init__(self, rates_to_usd: dict[Currency, Decimal]) -> None:
        """Initialize the rate converter.

        Args:
            rates_to_usd: Exchange rates where each value represents
                          how many USD 1 unit of that currency equals.
                          Example: {Currency.BTC: Decimal("95000")} means 1 BTC = 95000 USD

        Raises:
            ValueError: If USD rate is not 1 or any rate is non-positive.
        """
        if rates_to_usd.get(Currency.USD) != Decimal("1"):
            raise ValueError("USD 必須為基準貨幣，匯率必須為 1")
        if any(rate <= 0 for rate in rates_to_usd.values()):
            raise ValueError("所有匯率必須為正數")
        self._rates = rates_to_usd.copy()

    def convert(
        self,
        amount: Decimal,
        from_currency: Currency,
        to_currency: Currency,
    ) -> Decimal:
        """Convert an amount from one currency to another.

        Args:
            amount: The amount to convert.
            from_currency: The source currency.
            to_currency: The target currency.

        Returns:
            The converted amount in the target currency.

        Raises:
            ValueError: If either currency is not supported.
        """
        if from_currency not in self._rates or to_currency not in self._rates:
            raise ValueError(f"不支援的幣種：{from_currency} 或 {to_currency}")

        amount_in_usd = amount * self._rates[from_currency]
        return amount_in_usd / self._rates[to_currency]

    def get_rate(
        self,
        from_currency: Currency,
        to_currency: Currency,
    ) -> Decimal:
        """Get the exchange rate between two currencies.

        Args:
            from_currency: The source currency.
            to_currency: The target currency.

        Returns:
            The exchange rate (how many units of to_currency per 1 unit of from_currency).

        Raises:
            ValueError: If either currency is not supported.
        """
        if from_currency not in self._rates or to_currency not in self._rates:
            raise ValueError(f"不支援的幣種：{from_currency} 或 {to_currency}")
        return self._rates[from_currency] / self._rates[to_currency]


def get_default_converter() -> RateConverter:
    """Get a converter initialized with default exchange rates.

    Returns:
        A RateConverter instance with DEFAULT_RATES.
    """
    return RateConverter(DEFAULT_RATES)
