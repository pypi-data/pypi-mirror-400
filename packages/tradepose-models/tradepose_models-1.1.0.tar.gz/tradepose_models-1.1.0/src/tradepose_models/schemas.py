"""Shared data schemas and DTOs (共用數據模式).

This module contains Pydantic models for domain objects and data transfer
objects (DTOs) that are shared across multiple packages.

這個模組包含跨多個包共享的領域對象和數據傳輸對象（DTO）的 Pydantic 模型。

Example usage:
    from tradepose_models.schemas import PlanLimits, TaskResponse

    # Use in gateway to enforce limits
    limits = PlanLimits(
        max_requests_per_minute=100,
        max_concurrent_tasks=5
    )

    # Use in client to understand capabilities
    plan = client.get_plan()
    print(f"You can run {plan.limits.max_concurrent_tasks} tasks")
"""


# Placeholder for shared schemas
# Models will be migrated here from gateway as needed
# 共用模式將根據需要從 gateway 遷移到這裡

# Example structure:
# class PlanLimits(BaseModel):
#     """Rate limits and quotas for subscription plans."""
#     max_requests_per_minute: int
#     max_concurrent_tasks: int
#     max_strategies: int

__all__ = []
