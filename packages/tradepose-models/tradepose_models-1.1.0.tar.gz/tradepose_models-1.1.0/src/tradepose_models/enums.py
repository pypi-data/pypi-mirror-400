"""Shared enumerations (共用枚舉).

This module contains enum types that are used across multiple packages
to ensure consistency and type safety.

這個模組包含跨多個包使用的枚舉類型，以確保一致性和類型安全。

Example usage:
    from tradepose_models.enums import TaskStatus, PlanTier

    # Use in gateway
    task.status = TaskStatus.PROCESSING

    # Use in client
    if response.status == TaskStatus.COMPLETED:
        print("Task finished!")
"""


# Placeholder for shared enums
# Models will be migrated here from gateway as needed
# 共用枚舉將根據需要從 gateway 遷移到這裡

# Example structure:
# class TaskStatus(str, Enum):
#     """Task execution status."""
#     PENDING = "pending"
#     PROCESSING = "processing"
#     COMPLETED = "completed"
#     FAILED = "failed"

__all__ = []
