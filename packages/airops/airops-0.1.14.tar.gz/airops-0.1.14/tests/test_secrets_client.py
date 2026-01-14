"""Tests for Secrets client."""

from __future__ import annotations

import httpx
import pytest
from pytest_httpx import HTTPXMock

from airops.errors import (
    AuthError,
    RateLimitedError,
    SecretNotFoundError,
    UpstreamUnavailableError,
)
from airops.secrets.client import SecretMetadata, SecretsClient


def test_secret_metadata_dataclass() -> None:
    """SecretMetadata stores secret info."""
    metadata = SecretMetadata(
        id=1,
        name="MY_SECRET",
        type="workspace_secret",
        url="/internal_api/secrets/workspace_secrets/1",
    )
    assert metadata.id == 1
    assert metadata.name == "MY_SECRET"
    assert metadata.type == "workspace_secret"
    assert metadata.url == "/internal_api/secrets/workspace_secrets/1"
    assert metadata.provider is None


def test_secret_metadata_with_provider() -> None:
    """SecretMetadata stores provider for api_providers."""
    metadata = SecretMetadata(
        id=2,
        name="OpenAI",
        type="api_provider",
        url="/internal_api/secrets/api_providers/2",
        provider="open_ai",
    )
    assert metadata.provider == "open_ai"


@pytest.mark.asyncio
async def test_client_initialization(mock_env: None) -> None:
    """Client initializes with config."""
    client = SecretsClient()
    assert client._config.api_token == "test-token"
    await client.close()


@pytest.mark.asyncio
async def test_list_secrets(mock_env: None, httpx_mock: HTTPXMock) -> None:
    """List returns all secrets metadata."""
    httpx_mock.add_response(
        status_code=200,
        json={
            "secrets": [
                {
                    "id": 1,
                    "name": "MY_SECRET",
                    "type": "workspace_secret",
                    "url": "/internal_api/secrets/workspace_secrets/1",
                },
                {
                    "id": 2,
                    "name": "OpenAI",
                    "type": "api_provider",
                    "url": "/internal_api/secrets/api_providers/2",
                    "provider": "open_ai",
                },
            ]
        },
    )

    async with SecretsClient() as client:
        secrets = await client.list()

    assert len(secrets) == 2
    assert secrets[0].name == "MY_SECRET"
    assert secrets[0].type == "workspace_secret"
    assert secrets[1].name == "OpenAI"
    assert secrets[1].provider == "open_ai"


@pytest.mark.asyncio
async def test_get_workspace_secret_success(mock_env: None, httpx_mock: HTTPXMock) -> None:
    """Get workspace secret returns value."""
    httpx_mock.add_response(
        status_code=200,
        json={
            "secrets": [
                {
                    "id": 1,
                    "name": "MY_API_KEY",
                    "type": "workspace_secret",
                    "url": "/internal_api/secrets/workspace_secrets/1",
                },
            ]
        },
    )
    httpx_mock.add_response(
        status_code=200,
        json={
            "id": 1,
            "name": "MY_API_KEY",
            "type": "workspace_secret",
            "value": "secret-value-123",
        },
    )

    async with SecretsClient() as client:
        value = await client.get_workspace_secret("MY_API_KEY")

    assert value == "secret-value-123"


@pytest.mark.asyncio
async def test_get_workspace_secret_not_found(mock_env: None, httpx_mock: HTTPXMock) -> None:
    """Get workspace secret raises error when not found."""
    httpx_mock.add_response(
        status_code=200,
        json={"secrets": []},
    )

    async with SecretsClient() as client:
        with pytest.raises(SecretNotFoundError, match="Workspace secret 'MISSING' not found"):
            await client.get_workspace_secret("MISSING")


@pytest.mark.asyncio
async def test_get_api_provider_success(mock_env: None, httpx_mock: HTTPXMock) -> None:
    """Get API provider returns credentials dict."""
    httpx_mock.add_response(
        status_code=200,
        json={
            "secrets": [
                {
                    "id": 2,
                    "name": "OpenAI",
                    "type": "api_provider",
                    "url": "/internal_api/secrets/api_providers/2",
                    "provider": "open_ai",
                },
            ]
        },
    )
    httpx_mock.add_response(
        status_code=200,
        json={
            "id": 2,
            "name": "OpenAI",
            "provider": "open_ai",
            "type": "api_provider",
            "value": {"api_key": "sk-test-key"},
        },
    )

    async with SecretsClient() as client:
        creds = await client.get_api_provider("OpenAI")

    assert creds == {"api_key": "sk-test-key"}


@pytest.mark.asyncio
async def test_get_api_provider_not_found(mock_env: None, httpx_mock: HTTPXMock) -> None:
    """Get API provider raises error when not found."""
    httpx_mock.add_response(
        status_code=200,
        json={"secrets": []},
    )

    async with SecretsClient() as client:
        with pytest.raises(SecretNotFoundError, match="API provider 'Missing' not found"):
            await client.get_api_provider("Missing")


@pytest.mark.asyncio
async def test_get_api_provider_by_provider_success(mock_env: None, httpx_mock: HTTPXMock) -> None:
    """Get API provider by provider type returns credentials."""
    httpx_mock.add_response(
        status_code=200,
        json={
            "secrets": [
                {
                    "id": 2,
                    "name": "OpenAI",
                    "type": "api_provider",
                    "url": "/internal_api/secrets/api_providers/2",
                    "provider": "open_ai",
                },
            ]
        },
    )
    httpx_mock.add_response(
        status_code=200,
        json={
            "id": 2,
            "name": "OpenAI",
            "provider": "open_ai",
            "type": "api_provider",
            "value": {"api_key": "sk-test-key"},
        },
    )

    async with SecretsClient() as client:
        creds = await client.get_api_provider_by_provider("open_ai")

    assert creds == {"api_key": "sk-test-key"}


@pytest.mark.asyncio
async def test_get_api_provider_by_provider_not_found(
    mock_env: None, httpx_mock: HTTPXMock
) -> None:
    """Get API provider by provider type raises error when not found."""
    httpx_mock.add_response(
        status_code=200,
        json={"secrets": []},
    )

    async with SecretsClient() as client:
        with pytest.raises(SecretNotFoundError, match="API provider for 'anthropic' not found"):
            await client.get_api_provider_by_provider("anthropic")


@pytest.mark.asyncio
async def test_get_integration_auth_success(mock_env: None, httpx_mock: HTTPXMock) -> None:
    """Get integration auth returns credentials dict."""
    httpx_mock.add_response(
        status_code=200,
        json={
            "secrets": [
                {
                    "id": 3,
                    "name": "My Salesforce",
                    "type": "integration_authentication",
                    "url": "/internal_api/secrets/integration_authentications/3",
                    "provider": "Salesforce",
                },
            ]
        },
    )
    httpx_mock.add_response(
        status_code=200,
        json={
            "id": 3,
            "name": "My Salesforce",
            "provider": "Salesforce",
            "type": "integration_authentication",
            "value": {"access_token": "sf-token-123", "instance_url": "https://na1.salesforce.com"},
        },
    )

    async with SecretsClient() as client:
        creds = await client.get_integration_auth("My Salesforce")

    assert creds == {"access_token": "sf-token-123", "instance_url": "https://na1.salesforce.com"}


@pytest.mark.asyncio
async def test_get_integration_auth_not_found(mock_env: None, httpx_mock: HTTPXMock) -> None:
    """Get integration auth raises error when not found."""
    httpx_mock.add_response(
        status_code=200,
        json={"secrets": []},
    )

    async with SecretsClient() as client:
        with pytest.raises(
            SecretNotFoundError, match="Integration authentication 'Missing' not found"
        ):
            await client.get_integration_auth("Missing")


@pytest.mark.asyncio
async def test_401_raises_auth_error(mock_env: None, httpx_mock: HTTPXMock) -> None:
    """401 raises AuthError immediately without retry."""
    httpx_mock.add_response(status_code=401, text="Unauthorized")

    async with SecretsClient() as client:
        with pytest.raises(AuthError, match="Authentication failed"):
            await client._request_with_retry("GET", "/test")

    assert len(httpx_mock.get_requests()) == 1


@pytest.mark.asyncio
async def test_403_raises_auth_error(mock_env: None, httpx_mock: HTTPXMock) -> None:
    """403 raises AuthError immediately without retry."""
    httpx_mock.add_response(status_code=403, text="Forbidden")

    async with SecretsClient() as client:
        with pytest.raises(AuthError, match="Authentication failed"):
            await client._request_with_retry("GET", "/test")

    assert len(httpx_mock.get_requests()) == 1


@pytest.mark.asyncio
async def test_404_raises_secret_not_found_error(mock_env: None, httpx_mock: HTTPXMock) -> None:
    """404 raises SecretNotFoundError immediately without retry."""
    httpx_mock.add_response(status_code=404, text="Not Found")

    async with SecretsClient() as client:
        with pytest.raises(SecretNotFoundError, match="Resource not found"):
            await client._request_with_retry("GET", "/test")

    assert len(httpx_mock.get_requests()) == 1


@pytest.mark.asyncio
async def test_500_raises_upstream_error(mock_env: None, httpx_mock: HTTPXMock) -> None:
    """5xx raises UpstreamUnavailableError immediately without retry."""
    httpx_mock.add_response(status_code=500, text="Internal Server Error")

    async with SecretsClient() as client:
        with pytest.raises(UpstreamUnavailableError, match="Upstream unavailable"):
            await client._request_with_retry("GET", "/test")

    assert len(httpx_mock.get_requests()) == 1


@pytest.mark.asyncio
async def test_retry_on_429_then_success(
    mock_env: None, httpx_mock: HTTPXMock, no_retry_delay: None
) -> None:
    """429 triggers retry and succeeds on next attempt."""
    httpx_mock.add_response(status_code=429)
    httpx_mock.add_response(
        status_code=200,
        json={"secrets": []},
    )

    async with SecretsClient() as client:
        secrets = await client.list()
        assert secrets == []


@pytest.mark.asyncio
async def test_retry_exhausted_raises_rate_limit_error(
    mock_env: None, httpx_mock: HTTPXMock, no_retry_delay: None
) -> None:
    """Exhausted 429 retries raises RateLimitedError."""
    for _ in range(6):
        httpx_mock.add_response(status_code=429)

    async with SecretsClient() as client:
        with pytest.raises(RateLimitedError, match="Rate limit exceeded"):
            await client._request_with_retry("GET", "/test", max_retries=5)


@pytest.mark.asyncio
async def test_retry_on_network_error_then_success(
    mock_env: None, httpx_mock: HTTPXMock, no_retry_delay: None
) -> None:
    """Network error triggers retry and succeeds on next attempt."""
    httpx_mock.add_exception(httpx.ConnectError("Connection refused"))
    httpx_mock.add_response(
        status_code=200,
        json={"secrets": []},
    )

    async with SecretsClient() as client:
        secrets = await client.list()
        assert secrets == []


@pytest.mark.asyncio
async def test_network_error_exhausted_raises_upstream_error(
    mock_env: None, httpx_mock: HTTPXMock, no_retry_delay: None
) -> None:
    """Exhausted network error retries raises UpstreamUnavailableError."""
    for _ in range(6):
        httpx_mock.add_exception(httpx.ConnectError("Connection refused"))

    async with SecretsClient() as client:
        with pytest.raises(UpstreamUnavailableError, match="Network error"):
            await client._request_with_retry("GET", "/test", max_retries=5)
