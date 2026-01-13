"""Global configuration system for AG2 CLI with platform detection."""

from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


# Configuration file paths
CONFIG_DIR = Path.home() / ".ag2"
CONFIG_FILE = CONFIG_DIR / "config.ini"
DEFAULT_PROFILE = "default"


class Platform(str, Enum):
    """Supported deployment platforms."""

    FLY_IO = "fly"
    LOCAL = "local"
    UNKNOWN = "unknown"


class AG2Config(BaseSettings):
    """
    Global configuration for AG2 CLI.

    Automatically detects deployment platform and populates server URLs.
    Supports environment variable overrides with AG2_ prefix.
    """

    model_config = SettingsConfigDict(
        env_prefix="AG2_",
        case_sensitive=False,
    )

    platform: Optional[Platform] = None
    server_url: Optional[str] = None
    agentos_base_url: str = "http://localhost:3000"  # Base URL for AgentOS server
    provider_name: Optional[str] = None
    api_url: str = "http://localhost:8081/provisioner"  # Agent worker provisioner API URL
    worker_api_key: Optional[str] = None  # API key for worker heartbeats (from AG2_WORKER_API_KEY)

    def __init__(self, **kwargs) -> None:  # type: ignore[no-untyped-def]
        """Initialize config with platform detection and URL resolution."""
        super().__init__(**kwargs)
        if not self.platform:
            self.platform = self._detect_platform()


        if self.platform == Platform.FLY_IO and not self.provider_name:
            self.provider_name = os.getenv("FLY_APP_NAME")
        
        if not self.server_url:
            self.server_url = self._resolve_server_url()
        

        self.worker_api_key = os.getenv("AG2_WORKER_API_KEY")

    def _detect_platform(self) -> Platform:
        """Detect the current deployment platform from environment variables."""
        if os.getenv("FLY_APP_NAME"):
            return Platform.FLY_IO
        return Platform.LOCAL

    def _resolve_server_url(self) -> str:
        """Resolve the server URL based on detected platform."""
        if self.platform == Platform.FLY_IO and self.provider_name:
            return f"https://{self.provider_name}.fly.dev"
        return "http://localhost:8000"


# Global config singleton
_config: Optional[AG2Config] = None


def get_config() -> AG2Config:
    """
    Get the global AG2 configuration singleton.

    Returns:
        AG2Config: The global configuration instance
    """
    global _config
    if _config is None:
        _config = AG2Config()
    return _config


def reload_config() -> AG2Config:
    """
    Reload the global configuration from environment variables.

    Useful for testing or when environment variables change.

    Returns:
        AG2Config: The new configuration instance
    """
    global _config
    _config = AG2Config()
    return _config
