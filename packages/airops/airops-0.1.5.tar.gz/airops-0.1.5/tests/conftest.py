"""Pytest fixtures for AirOps SDK tests."""

from __future__ import annotations

import asyncio
from collections.abc import Generator
from unittest.mock import patch

import pytest

from airops.config import reset_config
from airops.server.store import reset_store
from airops.steps import reset as reset_steps


def _run_async(coro):  # type: ignore[no-untyped-def]
    """Run an async function synchronously."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is not None:
        # Already in an event loop, create a task
        return loop.run_until_complete(coro)
    else:
        return asyncio.run(coro)


@pytest.fixture(autouse=True)
def clean_state() -> Generator[None]:
    """Reset global state before each test."""
    reset_config()
    reset_store()
    _run_async(reset_steps())
    yield
    reset_config()
    reset_store()
    _run_async(reset_steps())


@pytest.fixture
def mock_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up mock environment variables."""
    monkeypatch.setenv("AIROPS_API_TOKEN", "test-token")
    monkeypatch.setenv("AIROPS_API_BASE_URL", "https://test.airops.com")


@pytest.fixture
def no_retry_delay() -> Generator[None]:
    """Disable retry delays for faster tests."""

    async def instant_sleep(seconds: float) -> None:
        pass

    with patch("asyncio.sleep", instant_sleep):
        yield
