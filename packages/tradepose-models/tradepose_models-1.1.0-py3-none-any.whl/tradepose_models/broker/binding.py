"""
Account-Portfolio Binding Model

Provides the AccountPortfolioBinding model for linking trading accounts to portfolios.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from ..enums import ExecutionMode


class AccountPortfolioBinding(BaseModel):
    """Account-Portfolio binding configuration.

    Links a trading account to a portfolio for automated trading.
    Controls execution behavior and capital allocation.

    Unique constraint: (account_id, portfolio_id)
    """

    id: UUID = Field(..., description="Binding UUID (primary key)")
    user_id: UUID = Field(..., description="User UUID for multi-tenancy")
    account_id: UUID = Field(..., description="Trading account UUID (FK)")
    portfolio_id: UUID = Field(..., description="Portfolio UUID (FK)")
    is_active: bool = Field(default=True, description="Whether binding is active")

    capital_override: Optional[Decimal] = Field(
        None, description="Override portfolio capital for this binding"
    )
    execution_mode: ExecutionMode = Field(
        default=ExecutionMode.PRICE_PRIORITY,
        description="Execution mode (price_priority or signal_priority)",
    )
    order_split_config: Optional[dict] = Field(
        None, description="Order split configuration (reserved for future use)"
    )

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    @property
    def is_price_priority(self) -> bool:
        """Check if execution mode is price priority."""
        return self.execution_mode == ExecutionMode.PRICE_PRIORITY

    @property
    def is_signal_priority(self) -> bool:
        """Check if execution mode is signal priority."""
        return self.execution_mode == ExecutionMode.SIGNAL_PRIORITY
