"""
Task status enumeration for export tasks
"""

from enum import Enum


class TaskStatus(int, Enum):
    """任務狀態枚舉（與 Worker TaskStatus enum 一致）

    對應 Worker 的 TaskStatus enum，用於追蹤 export 任務的執行狀態

    Rust 對應關係（#[repr(i16)]）:
    - Rust: TaskStatus::Pending    = 0 → Python: TaskStatus.PENDING    = 0
    - Rust: TaskStatus::Processing = 1 → Python: TaskStatus.PROCESSING = 1
    - Rust: TaskStatus::Completed  = 2 → Python: TaskStatus.COMPLETED  = 2
    - Rust: TaskStatus::Failed     = 3 → Python: TaskStatus.FAILED     = 3
    """

    PENDING = 0  # 待處理（Gateway 初始狀態）
    PROCESSING = 1  # 處理中（Worker 開始執行）
    COMPLETED = 2  # 已完成（Worker 成功完成）
    FAILED = 3  # 失敗（Worker 執行失敗或超時）
