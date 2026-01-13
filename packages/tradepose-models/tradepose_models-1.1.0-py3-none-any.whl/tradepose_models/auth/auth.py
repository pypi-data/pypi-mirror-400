"""Authentication context models."""

from uuid import UUID

from pydantic import BaseModel, Field


class AuthUser(BaseModel):
    """Authenticated user information."""

    user_id: str  # Clerk ID (primary key)
    auth_method: str = Field(..., description="Authentication method used: 'jwt' or 'api_key'")
    api_key_id: UUID | None = None  # Present if authenticated via API key


class AuthContext(BaseModel):
    """Full authentication context for a request."""

    user: AuthUser
    is_authenticated: bool = True
