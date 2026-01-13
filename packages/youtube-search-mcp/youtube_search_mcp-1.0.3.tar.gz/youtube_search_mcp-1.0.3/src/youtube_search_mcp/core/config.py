"""Configuration management using Pydantic Settings."""

import importlib.metadata
import os
from functools import lru_cache
from typing import Literal, TypedDict

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class _PackageMetadata(TypedDict):
    """Type definition for package metadata."""

    name: str
    version: str


@lru_cache(maxsize=1)
def get_package_metadata() -> _PackageMetadata:
    """
    Retrieve package metadata from the installed distribution.

    Falls back to default values if the package is not installed (e.g., in a development
    environment that is not an editable install).
    """
    try:
        dist = importlib.metadata.distribution("youtube-search-mcp")
        return {
            "name": dist.metadata["Name"],
            "version": dist.version,
        }
    except importlib.metadata.PackageNotFoundError:
        return {"name": "youtube-search-mcp-dev", "version": "1.0.0"}


_pkg_meta = get_package_metadata()


class Config(BaseSettings):
    """
    Application configuration with environment variable support.
    All settings can be overridden via environment variables with YT_MCP_ prefix.
    """

    # Server settings are loaded dynamically from pyproject.toml
    server_name: str = _pkg_meta["name"]
    server_version: str = _pkg_meta["version"]

    # Search settings
    default_max_results: int = 10
    max_results_limit: int = 50
    search_timeout: int = 30
    max_retries: int = 3

    # Download settings
    download_dir: str = "downloads"
    default_video_quality: Literal["best", "high", "medium", "low"] = "high"
    default_audio_quality: Literal["best", "high", "medium", "low"] = "high"
    default_video_format: str = "mp4"
    default_audio_format: str = "mp3"
    min_disk_space_mb: int = 100

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Output formatting
    default_format: Literal["json", "markdown"] = "json"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="YT_MCP_",
        case_sensitive=False,
    )

    @field_validator("download_dir", mode="after")
    @classmethod
    def expand_download_dir(cls, v: str) -> str:
        """
        Expand environment variables in download_dir.
        Supports %USERPROFILE% (Windows), $HOME (Linux/Mac), and ~ (home directory).
        """
        if not v:
            return v

        # Expand environment variables (Windows style %VAR% and Unix style $VAR)
        expanded = os.path.expandvars(v)

        # Expand user home directory (~)
        expanded = os.path.expanduser(expanded)

        return expanded

    def get(self, key: str, default: any = None) -> any:
        """Get configuration value by key."""
        return getattr(self, key, default)

    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value."""
        value = getattr(self, key, default)
        return int(value) if value is not None else default

    def get_str(self, key: str, default: str = "") -> str:
        """Get string configuration value."""
        value = getattr(self, key, default)
        return str(value) if value is not None else default


# Singleton instance
_config: Config | None = None


def get_config() -> Config:
    """
    Get or create configuration instance.

    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config()
    return _config


def reset_config() -> None:
    """Reset configuration instance (useful for testing)."""
    global _config
    _config = None
