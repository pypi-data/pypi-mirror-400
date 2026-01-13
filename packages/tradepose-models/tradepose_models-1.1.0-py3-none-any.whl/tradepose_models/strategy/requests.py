"""Strategy API request/response models."""

from uuid import UUID

from pydantic import BaseModel, Field


class RegisterStrategyRequest(BaseModel):
    """Request model for registering a strategy."""

    strategy_code: str = Field(..., description="Strategy configuration Python code")
    overwrite: bool = Field(default=False, description="Overwrite if strategy exists")


class RegisterStrategyResponse(BaseModel):
    """Response model for strategy registration."""

    task_id: UUID
    message: str


class ListStrategiesRequest(BaseModel):
    """Request model for listing strategies."""

    full: bool = Field(default=False, description="Return full configs or summary")
    instrument_id: str | None = Field(default=None, description="Filter by instrument ID")


class ListStrategiesResponse(BaseModel):
    """Response model for listing strategies."""

    task_id: UUID
    message: str
