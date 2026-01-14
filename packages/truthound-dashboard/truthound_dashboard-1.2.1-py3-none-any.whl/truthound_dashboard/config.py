"""Configuration settings with validation and extensibility.

This module provides a centralized configuration management system using
pydantic-settings for type-safe environment variable handling.

Example:
    # Get settings singleton
    settings = get_settings()

    # Access configuration
    print(settings.database_path)

    # Override via environment variables
    # TRUTHOUND_DATA_DIR=/custom/path
    # TRUTHOUND_PORT=9000
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Dashboard configuration settings.

    All settings can be overridden via environment variables with
    the TRUTHOUND_ prefix.

    Attributes:
        data_dir: Directory for storing database and cache files.
        host: Server host address.
        port: Server port number.
        log_level: Logging verbosity level.
        auth_enabled: Whether authentication is required.
        auth_password: Password for basic auth (if enabled).
        sample_size: Default sample size for validation.
        max_failed_rows: Maximum failed rows to store.
        default_timeout: Default timeout for operations in seconds.
    """

    model_config = SettingsConfigDict(
        env_prefix="TRUTHOUND_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Data storage
    data_dir: Path = Field(
        default_factory=lambda: Path.home() / ".truthound",
        description="Directory for database and cache files",
    )

    # Server configuration
    host: str = Field(default="127.0.0.1", description="Server host address")
    port: int = Field(default=8765, ge=1, le=65535, description="Server port")
    log_level: Literal["debug", "info", "warning", "error"] = Field(
        default="info", description="Logging level"
    )

    # Authentication (optional)
    auth_enabled: bool = Field(default=False, description="Enable authentication")
    auth_password: str | None = Field(
        default=None, description="Password for basic auth"
    )

    # Validation defaults
    sample_size: int = Field(
        default=10000, ge=100, description="Default sample size for validation"
    )
    max_failed_rows: int = Field(
        default=1000, ge=10, description="Maximum failed rows to store"
    )
    default_timeout: int = Field(
        default=300, ge=10, description="Default operation timeout in seconds"
    )

    # Worker configuration
    max_workers: int = Field(
        default=4, ge=1, le=32, description="Maximum worker threads"
    )

    @field_validator("data_dir", mode="before")
    @classmethod
    def expand_data_dir(cls, v: str | Path) -> Path:
        """Expand user home directory and resolve path."""
        return Path(v).expanduser().resolve()

    @property
    def database_path(self) -> Path:
        """Get SQLite database file path."""
        return self.data_dir / "dashboard.db"

    @property
    def cache_dir(self) -> Path:
        """Get cache directory path."""
        return self.data_dir / "cache"

    @property
    def schema_dir(self) -> Path:
        """Get schema storage directory path."""
        return self.data_dir / "schemas"

    def ensure_directories(self) -> None:
        """Create all required directories if they don't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.schema_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings singleton.

    Returns:
        Settings: The application settings instance.

    Note:
        This function is cached, so the settings are only loaded once.
        To reload settings, clear the cache with get_settings.cache_clear().
    """
    return Settings()


def reset_settings() -> None:
    """Reset settings cache for testing purposes."""
    get_settings.cache_clear()
