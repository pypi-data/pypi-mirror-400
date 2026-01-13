"""Gateway API Response Models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class OperationResponse(BaseModel):
    """Generic operation response with task ID."""

    task_id: str = Field(..., description="Task ID for polling status")
    message: str = Field(..., description="Human-readable message")


class StrategyOperationResponse(BaseModel):
    """Response for strategy operations (delete, get detail)."""

    task_id: str = Field(..., description="Task ID for polling status")
    message: str = Field(..., description="Operation status message")


class CancelSubscriptionResponse(BaseModel):
    """Response for subscription cancellation."""

    message: str = Field(..., description="Cancellation status message")
    status: str = Field(..., description="Updated subscription status")
    current_period_end: Optional[datetime] = Field(
        None, description="End of current billing period"
    )


class WebhookResponse(BaseModel):
    """Response for webhook processing."""

    status: str = Field(..., description="Processing status (success/error)")
    event: str = Field(..., description="Event type that was processed")
