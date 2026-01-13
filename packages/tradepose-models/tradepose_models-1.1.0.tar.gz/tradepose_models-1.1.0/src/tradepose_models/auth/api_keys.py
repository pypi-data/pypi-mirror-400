"""API key management models."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class APIKeyCreate(BaseModel):
    """Request model for creating a new API key."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Human-readable name for the API key",
    )


class APIKeyResponse(BaseModel):
    """Response model for API key (without plaintext key)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: str  # Clerk ID
    name: str
    revoked: bool
    last_used: datetime | None
    created_at: datetime


class APIKeyCreateResponse(BaseModel):
    """Response model when creating a new API key (includes plaintext key ONCE)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: str  # Clerk ID
    name: str
    api_key: str = Field(
        ...,
        description="Plaintext API key - save this securely, it won't be shown again!",
    )
    created_at: datetime


class APIKeyListResponse(BaseModel):
    """Response model for listing API keys."""

    keys: list[APIKeyResponse]
    total: int
