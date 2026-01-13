"""
PersistMode enum for export task persistence options.

Determines where backtest results are stored:
- REDIS: Default, stores Parquet in Redis (7-day TTL)
- PSQL: Dual-write to Redis + PostgreSQL trades table
"""

from enum import IntEnum


class PersistMode(IntEnum):
    """Persistence mode for backtest results.

    Used in ExportRequest to control where Worker stores trades data.

    Values:
        REDIS (0): Store only in Redis (Parquet format, default)
        PSQL (1): Dual-write to Redis (Parquet) + PostgreSQL (trades table)

    Examples:
        >>> from tradepose_models.enums import PersistMode
        >>> mode = PersistMode.REDIS  # Default
        >>> mode = PersistMode.PSQL   # Persist to PostgreSQL
    """

    REDIS = 0  # Default: Redis only (Parquet)
    PSQL = 1  # Dual-write: Redis + PostgreSQL trades table
