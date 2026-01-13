"""Engagement phase enum for 8-state lifecycle (Issue #305).

Represents the complete lifecycle of a trade engagement from creation
to closure, including failure states.
"""

from enum import IntEnum


class EngagementPhase(IntEnum):
    """Engagement phase (aligned with Rust #[repr(i16)]).

    8-state lifecycle for engagement execution tracking.
    Stored as SMALLINT in PostgreSQL.

    State transitions:
        PENDING(0) → ENTERING(1) → HOLDING(2) → EXITING(3) → CLOSED(4)
                         │                           │
                         ▼                           ▼
                     FAILED(5)                 EXIT_FAILED(7)

        CANCELLED(6) - Signal cancelled before execution
    """

    PENDING = 0
    """Initial state: Engagement created, awaiting entry order submission."""

    ENTERING = 1
    """Entry order submitted, waiting for fill."""

    HOLDING = 2
    """Entry filled, position is open and being held."""

    EXITING = 3
    """Exit order submitted (SL, TP, or manual), waiting for fill."""

    CLOSED = 4
    """Position fully closed (exit filled successfully)."""

    FAILED = 5
    """Entry failed (rejected, expired, or cancelled)."""

    CANCELLED = 6
    """Signal cancelled before entry (user or system action)."""

    EXIT_FAILED = 7
    """Exit failed but position may still be open (requires manual intervention)."""
