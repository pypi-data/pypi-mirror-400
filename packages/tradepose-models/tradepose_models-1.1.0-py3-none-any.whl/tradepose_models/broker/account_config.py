"""Broker account configuration models."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, SecretStr

from tradepose_models.enums import AccountSource, BrokerType


class MarketType(str, Enum):
    """Market types."""

    SPOT = "spot"  # Spot market
    FUTURES = "futures"  # Futures
    MARGIN = "margin"  # Margin trading
    OPTIONS = "options"  # Options
    SWAP = "swap"  # Perpetual swap


class AccountStatus(str, Enum):
    """Account status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    EXPIRED = "expired"


class BrokerCredentials(BaseModel):
    """
    Broker credentials (encrypted storage).

    Credentials are provided by users and passed to adapters.
    Storage encryption is handled by consuming applications.
    """

    api_key: SecretStr = Field(..., description="API Key")
    api_secret: SecretStr = Field(..., description="API Secret")

    # Optional fields (broker-specific)
    passphrase: Optional[SecretStr] = Field(None, description="API Passphrase (OKX)")
    account_id: Optional[str] = Field(None, description="Account ID")
    password: Optional[SecretStr] = Field(None, description="Login password (MT5)")
    person_id: Optional[str] = Field(None, description="Person ID (Taiwan brokers)")

    # Additional config
    extra_config: dict[str, Any] = Field(default_factory=dict)


class BrokerAccount(BaseModel):
    """
    Broker account configuration.

    This model is passed to BrokerAdapter on initialization.
    It contains all information needed to connect to a broker.
    """

    # Basic info
    id: UUID = Field(..., description="Account UUID")
    user_id: UUID = Field(..., description="User UUID who owns this account")
    name: str = Field(..., description="Account name")

    # Broker info (immutable after creation)
    broker_type: BrokerType = Field(..., description="Broker type")
    credentials: BrokerCredentials = Field(..., description="Encrypted credentials")

    # Market configuration
    available_markets: list[MarketType] = Field(
        ..., description="Supported market types for this account"
    )
    default_market: Optional[MarketType] = Field(None, description="Default market type")

    # Environment configuration
    environment: str = Field(
        default="production", description="Environment (production/testnet/sandbox)"
    )
    base_url: Optional[str] = Field(None, description="API Base URL")
    ws_url: Optional[str] = Field(None, description="WebSocket URL")

    # Status
    status: AccountStatus = Field(default=AccountStatus.INACTIVE)

    # Account source (for timezone handling)
    account_source: Optional[AccountSource] = Field(
        None, description="Account source (FTMO, IB, etc.) for timezone determination"
    )

    # Metadata
    created_at: datetime
    updated_at: datetime
