"""Subscription models."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .plans import PlanResponse


class SubscriptionResponse(BaseModel):
    """Response model for subscription (without sensitive data)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID  # User ID (UUID)
    lemonsqueezy_subscription_id: str | None = None
    lemonsqueezy_customer_id: str | None = None
    plan: str
    status: str
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None
    created_at: datetime
    updated_at: datetime


class SubscriptionDetailResponse(BaseModel):
    """Detailed subscription response with plan info."""

    subscription: SubscriptionResponse | None
    current_plan: PlanResponse
    usage_current_month: int = 0
    usage_limit: int = 0
