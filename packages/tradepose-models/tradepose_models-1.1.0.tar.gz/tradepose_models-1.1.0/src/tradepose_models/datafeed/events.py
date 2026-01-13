"""DataFeed event models for Redis Stream communication.

Security Design Principle:
    Events carry entity IDs only, never sensitive data like credentials.
    The consuming service (DataFeed) queries the database directly
    to retrieve sensitive data when needed.
"""

from datetime import datetime, timezone
from enum import StrEnum
from typing import Literal, Union
from uuid import UUID

from pydantic import BaseModel, Field


def _utc_now() -> datetime:
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


class DatafeedEventType(StrEnum):
    """DataFeed 事件類型"""

    INSTRUMENT_CRUD = "instrument_crud"
    OHLCV_DOWNLOAD = "ohlcv_download"
    BATCH_OHLCV_DOWNLOAD = "batch_ohlcv_download"


class InstrumentOperation(StrEnum):
    """Instrument CRUD 操作類型"""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SYNC = "sync"  # Scheduler 觸發的全量同步


class InstrumentCrudEvent(BaseModel):
    """Instrument CRUD 事件

    用於管理金融商品資料的新增、更新、刪除操作。
    - SYNC: 需要 account_id 來從 broker 下載所有商品
    - CREATE/UPDATE/DELETE: 需要 instrument_id 來操作單一商品

    Note: Uses IDs only - DataFeed queries DB for full objects.
    """

    event_type: Literal[DatafeedEventType.INSTRUMENT_CRUD] = DatafeedEventType.INSTRUMENT_CRUD
    task_id: str = Field(..., description="任務唯一識別碼")
    operation: InstrumentOperation = Field(..., description="CRUD 操作類型")

    # SYNC 操作需要 account_id 來連接 broker
    account_id: UUID | None = Field(default=None, description="Account UUID（SYNC 操作必填）")
    # CREATE/UPDATE/DELETE 操作需要 instrument_id
    instrument_id: int | None = Field(default=None, description="Instrument ID")

    created_at: datetime = Field(default_factory=_utc_now)
    retry_count: int = Field(default=0, description="重試次數")


class OHLCVDownloadEvent(BaseModel):
    """OHLCV 資料下載事件

    用於透過 BrokerAdapter 下載 OHLCV 資料並儲存到 PostgreSQL。

    Note: Uses IDs only - DataFeed queries DB for full objects.
    """

    event_type: Literal[DatafeedEventType.OHLCV_DOWNLOAD] = DatafeedEventType.OHLCV_DOWNLOAD
    task_id: str = Field(..., description="任務唯一識別碼")
    account_id: UUID = Field(..., description="Account UUID")

    # Instrument 識別（二選一）
    instrument_id: int | None = Field(default=None, description="Instrument ID")
    instrument_key: str | None = Field(
        default=None,
        description="Unique key: {source}:{market_type}:{symbol}",
    )

    timeframe: str = Field(..., description="時間框架 e.g., '1h', '4h', '1d'")
    start_time: datetime = Field(..., description="下載開始時間")
    end_time: datetime = Field(..., description="下載結束時間")
    created_at: datetime = Field(default_factory=_utc_now)
    retry_count: int = Field(default=0, description="重試次數")


class BatchOHLCVDownloadEvent(BaseModel):
    """批次 OHLCV 資料下載事件

    由 Scheduler 發送，包含多個 instruments 的下載任務。
    DataFeed 根據 broker_type 決定下載方式（MT5、Binance 等）。

    下載邏輯（由 DataFeed 處理）:
    1. 如果 force_full=True，忽略 DB 資料，從 start_time 完整下載
    2. 如果 DB 有該 instrument+freq 的資料，從 last_ts 開始增量下載
    3. 如果沒有資料且有 start_time，從 start_time 開始下載
    4. 否則使用 bars_count 從最新往回下載

    Note: Uses IDs only - DataFeed queries DB for full objects.
    """

    event_type: Literal[DatafeedEventType.BATCH_OHLCV_DOWNLOAD] = (
        DatafeedEventType.BATCH_OHLCV_DOWNLOAD
    )
    task_id: str = Field(..., description="任務唯一識別碼")
    account_id: UUID = Field(..., description="Account UUID")
    instrument_ids: list[int] = Field(..., description="Instrument ID 列表")

    # 下載參數
    timeframe: str = Field(default="1m", description="時間框架 e.g., '1m', '5m', '1h'")
    start_time: datetime | None = Field(
        default=None, description="起始時間（從 config 傳入，當 DB 無資料時使用）"
    )
    end_time: datetime | None = Field(
        default=None,
        description="結束時間（None = 下載到最新，自動填為 now + 30 天）",
    )
    bars_count: int | None = Field(
        default=None, description="K 線數量（從最新往回，當無 start_time 時的備用方案）"
    )
    force_full: bool = Field(
        default=False,
        description="強制完整下載（忽略 DB 現有資料，從 start_time 重新下載）",
    )

    created_at: datetime = Field(default_factory=_utc_now)
    retry_count: int = Field(default=0, description="重試次數")


# Union Type for Worker event dispatching
DatafeedEvent = Union[InstrumentCrudEvent, OHLCVDownloadEvent, BatchOHLCVDownloadEvent]
