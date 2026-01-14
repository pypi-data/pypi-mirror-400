"""Authentication handling for PlanVantage API."""

import os
from dataclasses import dataclass
from typing import Optional

from planvantage.exceptions import AuthenticationError


DEFAULT_BASE_URL = "https://api.planvantage.ai"
ENV_API_KEY = "PLANVANTAGE_API_KEY"
ENV_BASE_URL = "PLANVANTAGE_BASE_URL"


@dataclass
class AuthConfig:
    """Authentication configuration for API requests."""

    api_key: str
    base_url: str

    def __post_init__(self) -> None:
        """Validate configuration."""
        if not self.api_key:
            raise AuthenticationError(
                f"API key is required. Provide it via constructor or {ENV_API_KEY} environment variable."
            )
        # Ensure base_url doesn't have trailing slash
        self.base_url = self.base_url.rstrip("/")

    @classmethod
    def from_env(
        cls,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> "AuthConfig":
        """Create auth config from environment variables with optional overrides.

        Args:
            api_key: API key. Falls back to PLANVANTAGE_API_KEY env var.
            base_url: Base URL. Falls back to PLANVANTAGE_BASE_URL env var, then default.

        Returns:
            Configured AuthConfig instance.

        Raises:
            AuthenticationError: If no API key is provided or found in environment.
        """
        resolved_api_key = api_key or os.environ.get(ENV_API_KEY, "")
        resolved_base_url = (
            base_url
            or os.environ.get(ENV_BASE_URL, "")
            or DEFAULT_BASE_URL
        )
        return cls(api_key=resolved_api_key, base_url=resolved_base_url)

    def get_headers(self) -> dict[str, str]:
        """Get authentication headers for API requests.

        Returns:
            Dictionary of headers including Authorization bearer token.
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
