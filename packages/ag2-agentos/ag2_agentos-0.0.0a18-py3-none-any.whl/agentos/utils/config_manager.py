"""Configuration file management for AG2 CLI."""

from __future__ import annotations

import os
from configparser import ConfigParser
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()

# Configuration file paths
CONFIG_DIR = Path.home() / ".ag2"
CONFIG_FILE = CONFIG_DIR / "config.ini"
DEFAULT_PROFILE = "default"


class ConfigManager:
    """
    Manage AG2 CLI configuration in ~/.ag2/config.ini.

    Handles secure storage of access tokens with proper file permissions
    and supports multiple profiles for different environments.
    """

    def __init__(self, config_path: Path = CONFIG_FILE):
        """
        Initialize ConfigManager.

        Args:
            config_path: Path to config file (default: ~/.ag2/config.ini)
        """
        self.config_path = config_path
        self.parser = ConfigParser()

    def ensure_config_dir(self) -> None:
        """Create config directory with secure permissions if it doesn't exist."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Set directory permissions to 0700 (owner only)
        try:
            os.chmod(self.config_path.parent, 0o700)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not set directory permissions: {e}[/yellow]")

    def load(self) -> None:
        """Load config from file (creates empty config if file doesn't exist)."""
        if self.config_path.exists():
            try:
                self.parser.read(self.config_path)
            except Exception as e:
                console.print(f"[yellow]Warning: Failed to load config file: {e}[/yellow]")

    def save(self) -> None:
        """
        Save config to file with atomic write and secure permissions.

        Uses atomic write (write to temp file, then rename) to prevent
        corruption and sets file permissions to 0600 (owner read/write only).

        Raises:
            PermissionError: If unable to write to config directory
            OSError: If file write operation fails
        """
        try:
            self.ensure_config_dir()

            # Write to temporary file first (atomic write)
            temp_path = self.config_path.with_suffix('.tmp')

            with open(temp_path, 'w') as f:
                self.parser.write(f)

            # Set secure permissions (owner read/write only)
            os.chmod(temp_path, 0o600)

            # Atomic rename
            temp_path.rename(self.config_path)

        except PermissionError as e:
            console.print("[red]✗ Permission denied writing config file[/red]")
            console.print(f"[yellow]Please check permissions on {self.config_path}[/yellow]")
            raise
        except OSError as e:
            console.print(f"[red]✗ Failed to write config file: {e}[/red]")
            raise

    def set_access_token(
        self,
        token: str,
        profile: str = DEFAULT_PROFILE,
        api_url: Optional[str] = None,
    ) -> None:
        """
        Store access token in config file.

        Args:
            token: Access token to store
            profile: Profile name (default: "default")
            api_url: Optional API URL to store with token
        """
        if not self.parser.has_section(profile):
            self.parser.add_section(profile)

        self.parser.set(profile, "access_token", token)
        self.parser.set(profile, "created_at", datetime.now(timezone.utc).isoformat())

        if api_url:
            self.parser.set(profile, "api_url", api_url)

        self.save()

    def get_access_token(self, profile: str = DEFAULT_PROFILE) -> Optional[str]:
        """
        Retrieve access token from config.

        Args:
            profile: Profile name (default: "default")

        Returns:
            Access token if found, None otherwise
        """
        if self.parser.has_section(profile):
            return self.parser.get(profile, "access_token", fallback=None)
        return None

    def get_api_url(self, profile: str = DEFAULT_PROFILE) -> Optional[str]:
        """
        Retrieve API URL from config.

        Args:
            profile: Profile name (default: "default")

        Returns:
            API URL if found, None otherwise
        """
        if self.parser.has_section(profile):
            return self.parser.get(profile, "api_url", fallback=None)
        return None

    def clear_credentials(self, profile: str = DEFAULT_PROFILE) -> None:
        """
        Remove stored credentials for profile.

        Args:
            profile: Profile name (default: "default")
        """
        if self.parser.has_section(profile):
            self.parser.remove_section(profile)
            self.save()

    def has_credentials(self, profile: str = DEFAULT_PROFILE) -> bool:
        """
        Check if credentials exist for profile.

        Args:
            profile: Profile name (default: "default")

        Returns:
            True if credentials exist, False otherwise
        """
        return self.get_access_token(profile) is not None


# Global singleton instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """
    Get the global ConfigManager singleton instance.

    Returns:
        ConfigManager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
