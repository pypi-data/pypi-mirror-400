"""Connection status enum for broker adapters."""

from enum import Enum


class ConnectionStatus(str, Enum):
    """Broker connection status states."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"
    SCHEDULED_DOWNTIME = "scheduled_downtime"
