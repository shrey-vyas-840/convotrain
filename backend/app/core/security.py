"""Security helpers for password hashing and JWT handling.

These functions are intentionally independent from the database and API layer so
later authentication work can reuse them without refactoring.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.settings import get_settings

try:  # pragma: no cover - optional during bootstrap
    from jose import JWTError, jwt
except Exception:  # noqa: BLE001
    JWTError = Exception  # type: ignore[assignment]
    jwt = None  # type: ignore[assignment]

try:  # pragma: no cover - optional during bootstrap
    from passlib.context import CryptContext
except Exception:  # noqa: BLE001
    CryptContext = None  # type: ignore[assignment]

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") if CryptContext else None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if _pwd_context is None:
        raise RuntimeError("passlib is not installed")
    return _pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    if _pwd_context is None:
        raise RuntimeError("passlib is not installed")
    return _pwd_context.hash(password)


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    if jwt is None:
        raise RuntimeError("python-jose is not installed")

    settings = get_settings()
    now = datetime.now(timezone.utc)
    expiry = expires_delta or timedelta(minutes=settings.access_token_expiry_minutes)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + expiry).timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    if jwt is None:
        raise RuntimeError("python-jose is not installed")

    settings = get_settings()
    try:
        decoded = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        if not isinstance(decoded, dict):
            raise ValueError("Token payload must be a JSON object")
        return decoded
    except JWTError as exc:  # pragma: no cover - thin wrapper
        raise ValueError("Invalid access token") from exc
