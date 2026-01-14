"""Tests for Steps client."""

from __future__ import annotations

import httpx
import pytest
from pytest_httpx import HTTPXMock

from airops.config import ConfigError, get_config, reset_config
from airops.errors import (
    AuthError,
    InvalidInputError,
    RateLimitedError,
    UpstreamUnavailableError,
)
from airops.steps.client import StepHandle, StepsClient, StepStatus


def test_config_requires_token() -> None:
    """Config raises error without token."""
    reset_config()
    with pytest.raises(ConfigError, match="AIROPS_API_TOKEN"):
        get_config()


def test_config_loads_from_env(mock_env: None) -> None:
    """Config loads from environment."""
    config = get_config()
    assert config.api_token == "test-token"
    assert config.api_base_url == "https://test.airops.com"


def test_step_handle_dataclass() -> None:
    """StepHandle stores execution ID."""
    handle = StepHandle(step_execution_id="exec-123")
    assert handle.step_execution_id == "exec-123"


def test_step_status_dataclass() -> None:
    """StepStatus stores execution state."""
    status = StepStatus(
        step_execution_id="exec-123",
        status="success",
        outputs={"result": "value"},
    )
    assert status.step_execution_id == "exec-123"
    assert status.status == "success"
    assert status.outputs == {"result": "value"}
    assert status.error is None


@pytest.mark.asyncio
async def test_client_initialization(mock_env: None) -> None:
    """Client initializes with config."""
    client = StepsClient()
    assert client._config.api_token == "test-token"
    await client.close()


@pytest.mark.asyncio
async def test_retry_on_429_then_success(
    mock_env: None, httpx_mock: HTTPXMock, no_retry_delay: None
) -> None:
    """429 triggers retry and succeeds on next attempt."""
    httpx_mock.add_response(status_code=429)
    httpx_mock.add_response(
        status_code=200,
        json={"step_execution_id": "exec-123"},
    )

    async with StepsClient() as client:
        handle = await client.start("google_search", {"query": "test"})
        assert handle.step_execution_id == "exec-123"


@pytest.mark.asyncio
async def test_retry_exhausted_raises_rate_limit_error(
    mock_env: None, httpx_mock: HTTPXMock, no_retry_delay: None
) -> None:
    """Exhausted 429 retries raises RateLimitedError."""
    for _ in range(6):
        httpx_mock.add_response(status_code=429)

    async with StepsClient() as client:
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
        json={"step_execution_id": "exec-123"},
    )

    async with StepsClient() as client:
        handle = await client.start("google_search", {"query": "test"})
        assert handle.step_execution_id == "exec-123"


@pytest.mark.asyncio
async def test_network_error_exhausted_raises_upstream_error(
    mock_env: None, httpx_mock: HTTPXMock, no_retry_delay: None
) -> None:
    """Exhausted network error retries raises UpstreamUnavailableError."""
    for _ in range(6):
        httpx_mock.add_exception(httpx.ConnectError("Connection refused"))

    async with StepsClient() as client:
        with pytest.raises(UpstreamUnavailableError, match="Network error"):
            await client._request_with_retry("GET", "/test", max_retries=5)


@pytest.mark.asyncio
async def test_401_raises_auth_error_no_retry(mock_env: None, httpx_mock: HTTPXMock) -> None:
    """401 raises AuthError immediately without retry."""
    httpx_mock.add_response(status_code=401, text="Unauthorized")

    async with StepsClient() as client:
        with pytest.raises(AuthError, match="Authentication failed"):
            await client._request_with_retry("GET", "/test")

    assert len(httpx_mock.get_requests()) == 1


@pytest.mark.asyncio
async def test_403_raises_auth_error_no_retry(mock_env: None, httpx_mock: HTTPXMock) -> None:
    """403 raises AuthError immediately without retry."""
    httpx_mock.add_response(status_code=403, text="Forbidden")

    async with StepsClient() as client:
        with pytest.raises(AuthError, match="Authentication failed"):
            await client._request_with_retry("GET", "/test")

    assert len(httpx_mock.get_requests()) == 1


@pytest.mark.asyncio
async def test_400_raises_invalid_input_error_no_retry(
    mock_env: None, httpx_mock: HTTPXMock
) -> None:
    """400 raises InvalidInputError immediately without retry."""
    httpx_mock.add_response(
        status_code=400,
        json={"message": "Invalid input", "violations": []},
    )

    async with StepsClient() as client:
        with pytest.raises(InvalidInputError, match="Invalid input"):
            await client._request_with_retry("GET", "/test")

    assert len(httpx_mock.get_requests()) == 1


@pytest.mark.asyncio
async def test_500_raises_upstream_error_no_retry(mock_env: None, httpx_mock: HTTPXMock) -> None:
    """5xx raises UpstreamUnavailableError immediately without retry."""
    httpx_mock.add_response(status_code=500, text="Internal Server Error")

    async with StepsClient() as client:
        with pytest.raises(UpstreamUnavailableError, match="Upstream unavailable"):
            await client._request_with_retry("GET", "/test")

    assert len(httpx_mock.get_requests()) == 1
