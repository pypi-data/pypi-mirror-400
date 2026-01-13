"""
Engagement Model (Issue #305, #320)

Provides the Engagement model for trade execution context.
Tracks the lifecycle of a trade from signal to completion.

8-Phase lifecycle:
    PENDING(0) → ENTERING(1) → HOLDING(2) → EXITING(3) → CLOSED(4)
                     │                           │
                     ▼                           ▼
                 FAILED(5)                 EXIT_FAILED(7)

    CANCELLED(6) - Signal cancelled before execution
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from ..enums import EngagementPhase, TradeDirection


class Engagement(BaseModel):
    """Trade execution context (Engagement).

    Represents the binding between a trade signal and its execution.
    One engagement can generate multiple orders (entry, SL, TP, exit).

    Unique constraint: (user_id, account_id, binding_id, portfolio_id, blueprint_id, trade_id)
    """

    id: UUID = Field(..., description="Engagement UUID (primary key)")
    user_id: UUID = Field(..., description="User UUID")
    account_id: UUID = Field(..., description="Trading account UUID")
    binding_id: UUID = Field(..., description="Account-Portfolio binding UUID")
    portfolio_id: UUID = Field(..., description="Portfolio UUID")
    blueprint_id: UUID = Field(..., description="Blueprint UUID")
    trade_id: UUID = Field(..., description="Trade UUID (FK to trades)")

    # FK fields for direct lookup
    strategy_id: Optional[UUID] = Field(None, description="Strategy UUID")
    portfolio_allocation_id: Optional[UUID] = Field(None, description="Portfolio allocation UUID")

    # Phase system (8 states) - Issue #305
    phase: EngagementPhase = Field(
        default=EngagementPhase.PENDING,
        description="Engagement phase (0-7): PENDING, ENTERING, HOLDING, EXITING, CLOSED, FAILED, CANCELLED, EXIT_FAILED",
    )

    # Latest tracking
    is_latest: bool = Field(
        default=True,
        description="True if this is the most recent engagement for this trade context",
    )

    # Position sizing (MAE-based calculation)
    target_quantity: Optional[Decimal] = Field(
        None,
        description="Calculated position size based on MAE formula",
    )

    # Trade direction and prices
    direction: Optional[TradeDirection] = Field(
        None,
        description="Trade direction: Long or Short",
    )
    entry_price: Optional[Decimal] = Field(
        None,
        description="Target entry price from trade signal",
    )
    sl_price: Optional[Decimal] = Field(
        None,
        description="Stop loss price from trade signal",
    )
    tp_price: Optional[Decimal] = Field(
        None,
        description="Take profit price from trade signal",
    )

    # Fill tracking
    filled_entry_qty: Decimal = Field(
        default=Decimal("0"),
        description="Quantity filled for entry order",
    )
    filled_exit_qty: Decimal = Field(
        default=Decimal("0"),
        description="Quantity filled for exit order",
    )

    # Trading instrument (may differ from signal instrument)
    trading_instrument_id: Optional[int] = Field(
        None,
        description="Trading instrument ID (FK to data.instruments)",
    )
    symbol: Optional[str] = Field(
        None,
        description="Trading symbol for the mapped instrument",
    )

    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    # Phase helper properties
    @property
    def is_pending_phase(self) -> bool:
        """Check if engagement is in PENDING phase."""
        return self.phase == EngagementPhase.PENDING

    @property
    def is_entering_phase(self) -> bool:
        """Check if engagement is in ENTERING phase."""
        return self.phase == EngagementPhase.ENTERING

    @property
    def is_holding_phase(self) -> bool:
        """Check if engagement is in HOLDING phase (position open)."""
        return self.phase == EngagementPhase.HOLDING

    @property
    def is_exiting_phase(self) -> bool:
        """Check if engagement is in EXITING phase."""
        return self.phase == EngagementPhase.EXITING

    @property
    def is_closed_phase(self) -> bool:
        """Check if engagement is in CLOSED phase."""
        return self.phase == EngagementPhase.CLOSED

    @property
    def is_failed_phase(self) -> bool:
        """Check if engagement is in FAILED phase."""
        return self.phase == EngagementPhase.FAILED

    @property
    def is_cancelled_phase(self) -> bool:
        """Check if engagement is in CANCELLED phase."""
        return self.phase == EngagementPhase.CANCELLED

    @property
    def is_exit_failed_phase(self) -> bool:
        """Check if engagement is in EXIT_FAILED phase."""
        return self.phase == EngagementPhase.EXIT_FAILED

    @property
    def is_terminal(self) -> bool:
        """Check if engagement is in a terminal state (no more transitions)."""
        return self.phase in (
            EngagementPhase.CLOSED,
            EngagementPhase.FAILED,
            EngagementPhase.CANCELLED,
        )

    @property
    def needs_intervention(self) -> bool:
        """Check if engagement needs manual intervention."""
        return self.phase == EngagementPhase.EXIT_FAILED
