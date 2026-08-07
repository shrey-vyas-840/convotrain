"""Compatibility layer for application configuration imports."""

from app.core.settings import Settings, get_settings

settings = get_settings()

__all__ = ["Settings", "get_settings", "settings"]
