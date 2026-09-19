"""Authentication request and response schemas."""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Credentials submitted during login."""

    email: str = Field(min_length=1)
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    """JWT access-token response."""

    access_token: str
    token_type: str = "bearer"


class CurrentUserResponse(BaseModel):
    """Public representation of the authenticated user."""

    id: str
    full_name: str
    email: str
    platform_role: str
    is_active: bool
    is_email_verified: bool