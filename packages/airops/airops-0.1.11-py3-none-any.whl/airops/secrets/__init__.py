"""AirOps Secrets client module (stub for POC).

This module will provide access to workspace secrets and provider keys.
Currently not implemented.

Usage:
    from airops import secrets

    api_key = secrets.get("MY_API_KEY")
    provider_key = secrets.get_provider_key("openai")
"""

from __future__ import annotations

__all__ = ["get", "get_provider_key"]


def get(name: str) -> str:
    """Fetch a workspace secret by name.

    Args:
        name: The name of the secret to fetch.

    Returns:
        The secret value.

    Raises:
        NotImplementedError: This feature is not yet implemented.
    """
    raise NotImplementedError(
        "Secrets API is not yet implemented. For now, use environment variables directly."
    )


def get_provider_key(provider: str) -> str:
    """Fetch a provider API key.

    Args:
        provider: The provider name (e.g., "openai", "anthropic").

    Returns:
        The provider API key.

    Raises:
        NotImplementedError: This feature is not yet implemented.
    """
    raise NotImplementedError(
        "Secrets API is not yet implemented. For now, use environment variables directly."
    )
