from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import httpx

from airops.config import Config
from airops.errors import SecretNotFoundError
from airops.http import BaseClient

logger = logging.getLogger(__name__)


@dataclass
class SecretMetadata:
    """Metadata for a secret (from index endpoint)."""

    id: int
    name: str
    type: str
    url: str
    provider: str | None = None


class SecretsClient(BaseClient):
    """Client for fetching AirOps secrets."""

    def __init__(self, config: Config | None = None) -> None:
        super().__init__(config)

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle 404 SecretNotFoundError for secrets API."""
        if response.status_code == 404:
            raise SecretNotFoundError(f"Resource not found: {response.url.path}")

    async def list(self) -> list[SecretMetadata]:
        """List all secrets (without values).

        Returns:
            List of secret metadata.
        """
        logger.info("Listing secrets")
        response = await self._request_with_retry("GET", "/internal_api/secrets")
        data = response.json()

        secrets = []
        for item in data.get("secrets", []):
            secrets.append(
                SecretMetadata(
                    id=item["id"],
                    name=item["name"],
                    type=item["type"],
                    url=item["url"],
                    provider=item.get("provider"),
                )
            )

        logger.info("Found %d secrets", len(secrets))
        return secrets

    async def get_workspace_secret(self, name: str) -> str:
        """Fetch a workspace secret by name.

        Args:
            name: The name of the workspace secret.

        Returns:
            The secret value.

        Raises:
            SecretNotFoundError: If no workspace secret with this name exists.
        """
        logger.info("Getting workspace secret: %s", name)
        secrets = await self.list()

        for secret in secrets:
            if secret.type == "workspace_secret" and secret.name == name:
                data = await self._fetch_secret_value(secret.url)
                return str(data["value"])

        raise SecretNotFoundError(f"Workspace secret '{name}' not found")

    async def get_api_provider(self, name: str) -> dict[str, Any]:
        """Fetch an API provider by name.

        Args:
            name: The display name of the API provider.

        Returns:
            The credentials dict.

        Raises:
            SecretNotFoundError: If no API provider with this name exists.
        """
        logger.info("Getting API provider: %s", name)
        secrets = await self.list()

        for secret in secrets:
            if secret.type == "api_provider" and secret.name == name:
                data = await self._fetch_secret_value(secret.url)
                return dict(data["value"])

        raise SecretNotFoundError(f"API provider '{name}' not found")

    async def get_api_provider_by_provider(self, provider: str) -> dict[str, Any]:
        """Fetch an API provider by provider type.

        Args:
            provider: The provider type (e.g., "open_ai", "anthropic").

        Returns:
            The credentials dict.

        Raises:
            SecretNotFoundError: If no API provider with this type exists.
        """
        logger.info("Getting API provider by provider type: %s", provider)
        secrets = await self.list()

        for secret in secrets:
            if secret.type == "api_provider" and secret.provider == provider:
                data = await self._fetch_secret_value(secret.url)
                return dict(data["value"])

        raise SecretNotFoundError(f"API provider for '{provider}' not found")

    async def get_integration_auth(self, name: str) -> dict[str, Any]:
        """Fetch an integration authentication by name.

        Args:
            name: The name of the integration authentication.

        Returns:
            The credentials dict.

        Raises:
            SecretNotFoundError: If no integration auth with this name exists.
        """
        logger.info("Getting integration auth: %s", name)
        secrets = await self.list()

        for secret in secrets:
            if secret.type == "integration_authentication" and secret.name == name:
                data = await self._fetch_secret_value(secret.url)
                return dict(data["value"])

        raise SecretNotFoundError(f"Integration authentication '{name}' not found")

    async def _fetch_secret_value(self, url: str) -> dict[str, Any]:
        """Fetch the full secret details from a URL path."""
        response = await self._request_with_retry("GET", url)
        return dict(response.json())
