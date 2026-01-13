"""Currency enumeration for trading platforms."""

from enum import StrEnum


class Currency(StrEnum):
    """貨幣類型"""

    USD = "USD"
    USDT = "USDT"
    TWD = "TWD"
    EUR = "EUR"
    JPY = "JPY"
    BTC = "BTC"
    ETH = "ETH"
    XAU = "XAU"  # Gold
    TAIEX = "TAIEX"  # Taiwan Index
