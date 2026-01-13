"""Result models for scheduler operations."""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class OperationStatus(str, Enum):
    """Status of an operation."""

    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    FAILED = "failed"


class UpdateTradesResult(BaseModel):
    """Result of updating trades for a user.

    Returned by TradesUpdaterService.update_trades_for_user()
    """

    status: OperationStatus = Field(..., description="Operation status")
    user_id: str = Field(..., description="User UUID")
    sb_combinations: int = Field(..., description="Number of strategy+blueprint combinations found")
    batches_published: int = Field(..., description="Number of batches successfully published")
    tasks_published: list[str] = Field(
        default_factory=list, description="List of task IDs published"
    )
    errors: list[str] | None = Field(None, description="List of errors encountered (if any)")
    error: str | None = Field(None, description="Fatal error message (if failed)")

    model_config = ConfigDict(use_enum_values=True)


class TradesUpdateJobResult(BaseModel):
    """Result of TradesUpdateJob execution.

    Returned by TradesUpdateJob.run()
    """

    status: OperationStatus = Field(..., description="Job execution status")
    users_processed: int = Field(..., description="Number of users processed")
    total_batches: int = Field(..., description="Total batches published across all users")
    lookback_days: int = Field(..., description="Lookback period used")
    errors: list[str] | None = Field(None, description="List of errors encountered (if any)")
    error: str | None = Field(None, description="Fatal error message (if failed)")
    message: str | None = Field(None, description="Additional message (if applicable)")

    model_config = ConfigDict(use_enum_values=True)
