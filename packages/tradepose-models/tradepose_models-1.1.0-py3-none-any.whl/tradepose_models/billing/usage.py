"""Usage tracking models."""

from datetime import date, datetime

from pydantic import BaseModel, Field


class UsageDayResponse(BaseModel):
    """Daily usage record response."""

    usage_date: date = Field(..., description="Date of usage")
    requests: int = Field(..., description="Number of requests on this date")


class CurrentUsageResponse(BaseModel):
    """Current month usage response."""

    user_id: str  # Clerk ID
    current_month: str = Field(..., description="Current month (YYYY-MM)")
    usage: int = Field(..., description="Total requests this month")
    limit: int = Field(..., description="Monthly quota limit")
    remaining: int = Field(..., description="Remaining requests")
    percentage_used: float = Field(..., description="Percentage of quota used (0-100)")


class UsageHistoryResponse(BaseModel):
    """Historical usage response."""

    user_id: str  # Clerk ID
    start_date: date
    end_date: date
    total_requests: int = Field(..., description="Total requests in date range")
    daily_usage: list[UsageDayResponse] = Field(default_factory=list, description="Daily breakdown")


class UsageStatsResponse(BaseModel):
    """Usage statistics response."""

    current_month: CurrentUsageResponse
    plan_name: str
    plan_tier: str
    rate_limit_per_minute: int
    monthly_quota: int


class UsageWindowResponse(BaseModel):
    """Usage window response for a specific time period."""

    total_requests: int = Field(..., description="Total number of requests")
    completed_tasks: int = Field(..., description="Number of completed tasks")
    failed_tasks: int = Field(..., description="Number of failed tasks")


class DetailedUsageResponse(BaseModel):
    """Detailed usage statistics response from Redis cache."""

    period_start: datetime = Field(..., description="Start of the current billing period")
    last_minute: UsageWindowResponse = Field(..., description="Usage in the last minute")
    last_hour: UsageWindowResponse = Field(..., description="Usage in the last hour")
    last_day: UsageWindowResponse = Field(..., description="Usage in the last day")
    current_period: UsageWindowResponse = Field(
        ..., description="Usage in the current billing period"
    )
    plan: str = Field(..., description="Current plan tier (free/pro/enterprise)")
    monthly_quota: int = Field(..., description="Monthly quota limit for the plan")
    requests_per_minute: int = Field(..., description="Rate limit per minute")
    remaining_quota: int = Field(..., description="Remaining quota for the current period")
    quota_percentage_used: float = Field(
        ..., description="Percentage of monthly quota used (0-100)"
    )
    last_updated: datetime = Field(..., description="When this data was last calculated")
