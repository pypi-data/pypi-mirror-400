"""
Task Metadata Models

Provides two models for task metadata:
- TaskMetadata: Internal complete model (Gateway/Worker/Redis)
- TaskStatusResponse: Public API response (excludes internal fields)
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import Field

from ..base import BaseModel
from ..enums import ExportType, TaskStatus


class TaskMetadata(BaseModel):
    """
    Internal task metadata model (complete with all fields).

    This model is used for:
    1. Gateway creation - Initial task metadata
    2. Redis storage - Stored as JSON STRING
    3. Worker updates - Worker modifies status, timing, results
    4. Internal communication - Full context for backend

    For API responses, use TaskStatusResponse instead.
    """

    # Core identification
    task_id: UUID = Field(..., description="Task UUID")
    user_id: UUID = Field(description="User UUID (internal only, not included in API responses)")

    # Task status
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        description="Current task status (0=pending, 1=processing, 2=completed, 3=failed)",
    )

    # Operation info
    export_type: ExportType = Field(
        description="Export type (0=BACKTEST_RESULTS, 1=LATEST_TRADES, 2=ENHANCED_OHLCV, 3=ON_DEMAND_OHLCV)"
    )

    # Timing (TIMESTAMPTZ in PostgreSQL, datetime in Python, ISO 8601 in JSON)
    created_at: datetime = Field(..., description="Task creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Processing start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Processing completion timestamp")

    # Worker info
    worker_id: Optional[str] = Field(None, description="Worker ID that processed this task")

    # Strategy execution info
    executed_strategies: List[str] = Field(
        default_factory=list, description="List of strategy names that were executed"
    )
    strategy_counts: int = Field(
        default=0, description="Number of strategies (Gateway sets, Worker may update)"
    )
    blueprint_counts: int = Field(default=0, description="Number of blueprints processed")
    indicator_counts: int = Field(default=0, description="Number of indicators used")
    trigger_counts: int = Field(default=0, description="Number of triggers used")
    input_rows: int = Field(default=0, description="Number of input rows processed")

    # Error handling
    error_message: Optional[str] = Field(None, description="Error message if task failed")


class TaskMetadataResponse(TaskMetadata):
    """
    Public API response model for task metadata.

    Inherits from TaskMetadata but excludes internal-only fields.
    This model is returned by GET /api/v1/tasks/{task_id} endpoint.

    Excluded fields:
    - executed_strategies: Internal execution details
    - error_message: Internal error tracking
    """

    def model_dump(self, **kwargs):
        """Override to exclude internal-only fields from serialization."""
        data = super().model_dump(**kwargs)
        data.pop("executed_strategies", None)
        # data.pop("error_message", None)
        return data

    def model_dump_json(self, **kwargs):
        """Override JSON serialization to exclude internal-only fields."""
        exclude = kwargs.get("exclude", set())
        if isinstance(exclude, set):
            exclude.add("executed_strategies")
            # exclude.add("error_message")
        kwargs["exclude"] = exclude
        return super().model_dump_json(**kwargs)
