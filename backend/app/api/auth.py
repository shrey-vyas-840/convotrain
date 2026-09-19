"""Authentication API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    TokenResponse,
)
from app.services.auth import (
    authenticate_user,
    create_user_access_token,
)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["authentication"],
)


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Authenticate a user and return a JWT access token."""

    user = authenticate_user(
        db=db,
        email=payload.email,
        password=payload.password,
    )

    token = create_user_access_token(user)

    return TokenResponse(access_token=token)


@router.get("/me", response_model=CurrentUserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
) -> CurrentUserResponse:
    """Return the currently authenticated user."""

    return CurrentUserResponse(
        id=str(current_user.id),
        full_name=current_user.full_name,
        email=current_user.email,
        platform_role=current_user.platform_role,
        is_active=current_user.is_active,
        is_email_verified=current_user.is_email_verified,
    )