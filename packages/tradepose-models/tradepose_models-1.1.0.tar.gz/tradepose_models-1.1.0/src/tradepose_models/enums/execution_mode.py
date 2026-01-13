"""Execution mode enum for account-portfolio bindings."""

from enum import Enum


class ExecutionMode(str, Enum):
    """Binding execution mode.

    Determines how orders are executed when binding an account to a portfolio.
    """

    PRICE_PRIORITY = "price_priority"
    """Prioritize price execution (default). Wait for better price."""

    SIGNAL_PRIORITY = "signal_priority"
    """Prioritize signal execution. Execute immediately at market."""
