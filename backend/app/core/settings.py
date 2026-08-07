"""Application settings loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized runtime configuration.

    The defaults keep local development runnable while allowing environment
    variables to override every production-facing value.
    """

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = Field(default="Restaurant Knowledge OS")
    environment: Literal["development", "test", "staging", "production"] = Field(
        default="development"
    )
    debug: bool = Field(default=True)
    api_v1_prefix: str = Field(default="/api/v1")

    postgres_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/restaurant_knowledge_os"
    )
    jwt_secret_key: str = Field(default="change-me-in-production")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expiry_minutes: int = Field(default=60 * 24)

    qdrant_url: AnyHttpUrl = Field(default="http://localhost:6333")
    openai_api_key: str | None = Field(default=None)

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )

    @field_validator("postgres_url")
    @classmethod
    def validate_postgres_url(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("postgres_url must not be empty")
        return value

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("jwt_secret_key must not be empty")
        return value

    @field_validator("access_token_expiry_minutes")
    @classmethod
    def validate_token_expiry(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("access_token_expiry_minutes must be positive")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
