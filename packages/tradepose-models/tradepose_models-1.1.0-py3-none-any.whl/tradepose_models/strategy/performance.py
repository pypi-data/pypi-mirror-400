"""
Strategy Performance Model

Provides StrategyPerformance for caching strategy metrics in Redis.
Used for position size calculation and performance monitoring.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class StrategyPerformance(BaseModel):
    """Strategy performance metrics (Redis cache).

    Stores calculated performance metrics for a strategy+blueprint combination.
    Used by TradingDecisionJob for position size calculation.

    Redis Key Pattern: performance:{user_id}:{strategy_name}:{blueprint_name}
    """

    strategy_name: str = Field(..., description="Strategy name")
    blueprint_name: str = Field(..., description="Blueprint name")
    user_id: UUID = Field(..., description="User UUID")
    instrument: str = Field(..., description="Trading instrument (e.g., XAUUSD)")

    # Performance metrics
    win_rate: float = Field(..., description="Win rate (0-1)")
    avg_pnl_pct: float = Field(..., description="Average PnL percentage")
    mae_q90: float = Field(..., description="Maximum Adverse Excursion 90th percentile (%)")
    mfe_q90: float = Field(..., description="Maximum Favorable Excursion 90th percentile (%)")
    recovery_factor: float = Field(..., description="Recovery factor")

    # Position size calculation
    expected_loss_per_contract: Decimal = Field(
        ...,
        description="Expected loss per contract in quote currency (e.g., 40000 USD)",
    )
    quote_currency: str = Field(..., description="Quote currency (e.g., USD)")
    contract_size: Decimal = Field(..., description="Contract size per lot")

    # Cache metadata
    updated_at: datetime = Field(..., description="Last update timestamp")

    def calculate_position_size(self, risk_capital: Decimal) -> Decimal:
        """Calculate position size based on risk capital.

        Args:
            risk_capital: User's risk capital in portfolio currency

        Returns:
            Number of contracts/lots to trade

        Example:
            >>> perf = StrategyPerformance(
            ...     expected_loss_per_contract=Decimal("40000"),
            ...     ...
            ... )
            >>> qty = perf.calculate_position_size(Decimal("80000"))
            >>> # qty = 80000 / 40000 = 2 contracts
        """
        if self.expected_loss_per_contract <= 0:
            return Decimal("0")
        return risk_capital / self.expected_loss_per_contract
