"""Subscription plan models."""

from pydantic import BaseModel


class PlanLimitsResponse(BaseModel):
    """Plan limits response model."""

    requests_per_minute: int
    monthly_quota: int
    max_concurrent_tasks: int
    max_strategies: int
    priority_queue: bool
    support_level: str


class PlanResponse(BaseModel):
    """Subscription plan response model."""

    tier: str
    name: str
    description: str
    price_monthly: float
    price_yearly: float
    limits: PlanLimitsResponse
    features: list[str]


class PlansListResponse(BaseModel):
    """Response model for listing all plans."""

    plans: list[PlanResponse]
