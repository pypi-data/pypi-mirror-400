"""AirOps Secrets client module.

Usage:
    from airops import secrets

    # Get a workspace secret
    api_key = await secrets.get_workspace_secret("MY_API_KEY")

    # Get an API provider's credentials by display name
    creds = await secrets.get_api_provider("OpenAI")

    # Get an API provider's credentials by provider type
    creds = await secrets.get_provider_key("open_ai")

    # Get an integration authentication's credentials
    creds = await secrets.get_integration_auth("My Salesforce")
"""

from __future__ import annotations

from typing import Any

from airops.secrets.client import SecretMetadata, SecretsClient

__all__ = [
    "get_workspace_secret",
    "get_api_provider",
    "get_provider_key",
    "get_integration_auth",
    "list_secrets",
    "SecretMetadata",
]

_client: SecretsClient | None = None


def _get_client() -> SecretsClient:
    """Get or create the global SecretsClient instance."""
    global _client
    if _client is None:
        _client = SecretsClient()
    return _client


async def list_secrets() -> list[SecretMetadata]:
    """List all secrets (without values).

    Returns:
        List of secret metadata.

    Example:
        >>> from airops import secrets
        >>> all_secrets = await secrets.list_secrets()
    """
    return await _get_client().list()


async def get_workspace_secret(name: str) -> str:
    """Fetch a workspace secret by name.

    Args:
        name: The name of the workspace secret.

    Returns:
        The secret value.

    Raises:
        SecretNotFoundError: If no workspace secret with this name exists.

    Example:
        >>> from airops import secrets
        >>> api_key = await secrets.get_workspace_secret("MY_API_KEY")
    """
    return await _get_client().get_workspace_secret(name)


async def get_api_provider(name: str) -> dict[str, Any]:
    """Fetch an API provider's credentials by display name.

    Args:
        name: The display name of the API provider (e.g., "OpenAI", "Anthropic").

    Returns:
        The credentials dict containing keys like "api_key".

    Raises:
        SecretNotFoundError: If no API provider with this name exists.

    Example:
        >>> from airops import secrets
        >>> creds = await secrets.get_api_provider("OpenAI")
        >>> api_key = creds["api_key"]
    """
    return await _get_client().get_api_provider(name)


async def get_provider_key(provider: str) -> dict[str, Any]:
    """Fetch an API provider's credentials by provider type.

    Args:
        provider: The provider type (e.g., "open_ai", "anthropic", "pinecone").

    Returns:
        The credentials dict containing keys like "api_key".

    Raises:
        SecretNotFoundError: If no API provider for this type exists.

    Example:
        >>> from airops import secrets
        >>> creds = await secrets.get_provider_key("open_ai")
        >>> api_key = creds["api_key"]
    """
    return await _get_client().get_api_provider_by_provider(provider)


async def get_integration_auth(name: str) -> dict[str, Any]:
    """Fetch an integration authentication's credentials by name.

    Args:
        name: The name of the integration authentication.

    Returns:
        The credentials dict.

    Raises:
        SecretNotFoundError: If no integration auth with this name exists.

    Example:
        >>> from airops import secrets
        >>> creds = await secrets.get_integration_auth("My Salesforce")
    """
    return await _get_client().get_integration_auth(name)


async def reset() -> None:
    """Reset the global client (useful for testing)."""
    global _client
    if _client is not None:
        await _client.close()
        _client = None
