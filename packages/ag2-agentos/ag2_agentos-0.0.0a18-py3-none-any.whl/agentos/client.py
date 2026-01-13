"""HTTP client wrapper with automatic API key injection."""

from __future__ import annotations

import os
from typing import Any, Optional

import httpx
import keyring
from rich.console import Console

console = Console()

# Service name for keyring storage
KEYRING_SERVICE = "ag2-cli"
KEYRING_API_KEY = "api-key"
KEYRING_ORG_ID = "organization-id"


class AG2Client:
    """
    HTTP client wrapper that automatically injects API keys into requests.

    Stores API keys securely using the system keyring and automatically
    adds them to all requests as the X-API-Key header.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8085",
        api_key: Optional[str] = None,
        access_token: Optional[str] = None,
        organization_id: Optional[str] = None,
        timeout: float = 10.0,
        profile: str = "default",
    ):
        """
        Initialize the AG2 client.

        Authentication priority order:
        1. Explicit access_token parameter
        2. Explicit api_key parameter
        3. Config file access_token (from ~/.ag2/config.ini)
        4. AG2_WORKER_API_KEY environment variable (for workers)

        Args:
            base_url: Base URL for API requests
            api_key: API key (deprecated, primarily for workers)
            access_token: Access token from OAuth login
            organization_id: Organization ID (if not provided, loads from keyring)
            timeout: Request timeout in seconds
            profile: Config profile to use (default: "default")
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.profile = profile

        # Determine access token with priority order
        if access_token:
            self._access_token = access_token
        elif api_key:
            self._access_token = api_key
        else:
            # Try to load from config file
            try:
                from agentos.utils.config_manager import get_config_manager
                config_mgr = get_config_manager()
                config_mgr.load()
                self._access_token = config_mgr.get_access_token(profile)
            except Exception:
                self._access_token = None

            # Fallback to environment variable for workers
            if not self._access_token:
                self._access_token = os.getenv("AG2_WORKER_API_KEY")

            # Final fallback to keyring (for backward compatibility)
            if not self._access_token:
                self._access_token = self.get_stored_api_key()

        self._organization_id = organization_id or self.get_stored_organization_id()

    @property
    def api_key(self) -> Optional[str]:
        """Get the current API key (deprecated, use access_token)."""
        return self._access_token

    @property
    def access_token(self) -> Optional[str]:
        """Get the current access token."""
        return self._access_token

    @property
    def organization_id(self) -> Optional[str]:
        """Get the current organization ID."""
        return self._organization_id

    @staticmethod
    def get_stored_api_key() -> Optional[str]:
        """Retrieve API key from keyring storage."""
        try:
            return keyring.get_password(KEYRING_SERVICE, KEYRING_API_KEY)
        except Exception:
            return None

    @staticmethod
    def get_stored_organization_id() -> Optional[str]:
        """Retrieve organization ID from keyring storage."""
        try:
            return keyring.get_password(KEYRING_SERVICE, KEYRING_ORG_ID)
        except Exception:
            return None

    @staticmethod
    def store_api_key(api_key: str) -> None:
        """
        Store API key in keyring.

        Args:
            api_key: API key to store
        """
        try:
            keyring.set_password(KEYRING_SERVICE, KEYRING_API_KEY, api_key)
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to store API key in keyring: {e}[/yellow]")

    @staticmethod
    def store_organization_id(organization_id: str) -> None:
        """
        Store organization ID in keyring.

        Args:
            organization_id: Organization ID to store
        """
        try:
            keyring.set_password(KEYRING_SERVICE, KEYRING_ORG_ID, organization_id)
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to store organization ID in keyring: {e}[/yellow]")

    @staticmethod
    def clear_credentials() -> None:
        """Clear stored API key and organization ID from keyring."""
        try:
            keyring.delete_password(KEYRING_SERVICE, KEYRING_API_KEY)
        except Exception:
            pass
        try:
            keyring.delete_password(KEYRING_SERVICE, KEYRING_ORG_ID)
        except Exception:
            pass

    def _get_headers(self, additional_headers: Optional[dict[str, str]] = None) -> dict[str, str]:
        """
        Build request headers with access token.

        Args:
            additional_headers: Additional headers to include

        Returns:
            Complete headers dictionary
        """
        headers = {"Content-Type": "application/json"}

        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"

        if additional_headers:
            headers.update(additional_headers)

        return headers

    def request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[dict[str, str]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Make an HTTP request with automatic API key injection.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint (will be appended to base_url)
            headers: Additional headers
            **kwargs: Additional arguments to pass to httpx

        Returns:
            httpx.Response object

        Raises:
            httpx.HTTPStatusError: If response status is 4xx or 5xx
            httpx.RequestError: If request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = self._get_headers(headers)

        with httpx.Client(timeout=self.timeout) as client:
            response = client.request(
                method=method,
                url=url,
                headers=request_headers,
                **kwargs,
            )
            response.raise_for_status()
            return response

    def get(self, endpoint: str, **kwargs: Any) -> httpx.Response:
        """Make a GET request."""
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs: Any) -> httpx.Response:
        """Make a POST request."""
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs: Any) -> httpx.Response:
        """Make a PUT request."""
        return self.request("PUT", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> httpx.Response:
        """Make a DELETE request."""
        return self.request("DELETE", endpoint, **kwargs)

    def upload_file(
        self,
        endpoint: str,
        files: dict[str, Any],
        data: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Upload files with multipart/form-data.

        Args:
            endpoint: API endpoint
            files: Files to upload (dict of {field_name: (filename, file_obj, content_type)})
            data: Additional form data
            **kwargs: Additional arguments

        Returns:
            httpx.Response object
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Build headers without Content-Type (httpx sets it for multipart)
        headers = {}
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                url=url,
                files=files,
                data=data,
                headers=headers,
                **kwargs,
            )
            response.raise_for_status()
            return response


def get_client(
    base_url: str = "http://localhost:8085",
    api_key: Optional[str] = None,
    access_token: Optional[str] = None,
    organization_id: Optional[str] = None,
    profile: str = "default",
) -> AG2Client:
    """
    Get an AG2 client instance.

    Args:
        base_url: Base URL for API requests
        api_key: Optional API key (deprecated, primarily for workers)
        access_token: Optional access token from OAuth login
        organization_id: Optional organization ID (loads from keyring if not provided)
        profile: Config profile to use (default: "default")

    Returns:
        AG2Client instance
    """
    return AG2Client(
        base_url=base_url,
        api_key=api_key,
        access_token=access_token,
        organization_id=organization_id,
        profile=profile,
    )

def get_client_from_config() -> AG2Client:
    """
    Get an AG2 client instance using configuration from AG2Config.

    For workers: Uses AG2_WORKER_API_KEY environment variable
    For CLI: Uses access token from ~/.ag2/config.ini

    Returns:
        AG2Client instance
    """
    from agentos.config import get_config

    config = get_config()

    # Workers use API key from environment variable
    if config.worker_api_key:
        return AG2Client(
            base_url=config.api_url,
            api_key=config.worker_api_key,
        )

    # CLI uses access token from config file (loaded automatically by AG2Client)
    return AG2Client(
        base_url=config.api_url,
    )