from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any

import httpx
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

from airops.config import Config, get_config
from airops.errors import (
    AuthError,
    InvalidInputError,
    RateLimitedError,
    SchemaViolation,
    StepErrorDetails,
    StepFailedError,
    StepTimeoutError,
    UpstreamUnavailableError,
)

StepResult = dict[str, Any] | list[Any] | str


class _RetryableError(Exception):
    """Internal exception to signal retry."""

    def __init__(
        self,
        message: str,
        retry_after: float | None = None,
        is_rate_limit: bool = False,
    ) -> None:
        super().__init__(message)
        self.retry_after = retry_after
        self.is_rate_limit = is_rate_limit


def _wait_with_retry_after(retry_state: RetryCallState) -> float:
    """Wait strategy that respects Retry-After header."""
    exc = retry_state.outcome.exception() if retry_state.outcome else None
    if isinstance(exc, _RetryableError) and exc.retry_after is not None:
        return exc.retry_after
    return wait_exponential_jitter(initial=1, max=60)(retry_state)


@dataclass
class StepHandle:
    """Handle returned from starting a step execution."""

    step_execution_id: str


@dataclass
class StepStatus:
    """Status of a step execution."""

    step_execution_id: str
    status: str  # "running", "success", "error"
    outputs: dict[str, Any] | None = None
    error: StepErrorDetails | None = None


class StepsClient:
    """Client for executing AirOps steps via the Steps API."""

    def __init__(self, config: Config | None = None) -> None:
        self._config = config or get_config()
        self._client = httpx.AsyncClient(
            base_url=self._config.api_base_url,
            headers={
                "Authorization": f"Bearer {self._config.api_token}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def execute(
        self,
        step_type: str,
        inputs: dict[str, Any],
        timeout_s: int | None = None,
    ) -> StepResult:
        """Execute a step and wait for completion.

        Args:
            step_type: The type of step to execute (e.g., "google_search").
            inputs: Input parameters for the step.
            timeout_s: Maximum time to wait for completion (default: config default).

        Returns:
            The step outputs (dict, list, or string depending on step type).

        Raises:
            StepTimeoutError: If the step doesn't complete within the timeout.
            StepFailedError: If the step execution fails.
            InvalidInputError: If the step inputs are invalid.
            AuthError: If authentication fails.
            RateLimitedError: If rate limits are exhausted.
            UpstreamUnavailableError: If the API is unavailable.
        """
        handle = await self.start(step_type, inputs)

        timeout = timeout_s if timeout_s is not None else self._config.default_timeout_s
        deadline = time.monotonic() + timeout
        poll_interval = self._config.poll_interval_s

        while True:
            status = await self.poll(handle.step_execution_id)

            if status.status == "success":
                return status.outputs or {}

            if status.status == "error":
                err_msg = status.error.message if status.error else "unknown error"
                raise StepFailedError(
                    f"Step '{step_type}' failed: {err_msg}",
                    error_details=status.error,
                )

            if time.monotonic() >= deadline:
                raise StepTimeoutError(f"Step '{step_type}' did not complete within {timeout}s")

            await asyncio.sleep(poll_interval)
            poll_interval = min(poll_interval * 1.5, 10.0)

    async def start(self, step_type: str, inputs: dict[str, Any]) -> StepHandle:
        """Start a step execution.

        Args:
            step_type: The type of step to execute.
            inputs: Input parameters for the step.

        Returns:
            A handle containing the step_execution_id.
        """
        response = await self._request_with_retry(
            "POST",
            "/internal_api/steps/executions",
            json={"type": step_type, "inputs": inputs},
        )

        data = response.json()
        return StepHandle(step_execution_id=data["step_execution_id"])

    async def poll(self, step_execution_id: str) -> StepStatus:
        """Poll the status of a step execution.

        Args:
            step_execution_id: The ID of the step execution to poll.

        Returns:
            The current status of the execution.
        """
        response = await self._request_with_retry(
            "GET",
            f"/internal_api/steps/executions/{step_execution_id}",
        )

        data = response.json()
        error = None
        if data.get("error"):
            err = data["error"]
            error = StepErrorDetails(
                code=err.get("code", "unknown"),
                message=err.get("message", "Unknown error"),
                details=err.get("details"),
                retryable=err.get("retryable", False),
            )

        return StepStatus(
            step_execution_id=data["step_execution_id"],
            status=data["status"],
            outputs=data.get("outputs"),
            error=error,
        )

    async def _request_with_retry(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        max_retries: int = 60,
    ) -> httpx.Response:
        """Make an HTTP request with retry logic for rate limiting.

        Args:
            method: HTTP method.
            path: Request path.
            json: JSON body for the request.
            max_retries: Maximum number of retries for rate limiting.

        Returns:
            The HTTP response.

        Raises:
            AuthError: If authentication fails.
            InvalidInputError: If the request is invalid.
            RateLimitedError: If rate limits are exhausted.
            UpstreamUnavailableError: If the API is unavailable.
        """
        try:
            async for attempt in AsyncRetrying(
                retry=retry_if_exception_type(_RetryableError),
                stop=stop_after_attempt(max_retries + 1),
                wait=_wait_with_retry_after,
                reraise=True,
            ):
                with attempt:
                    return await self._make_request(method, path, json=json)
        except _RetryableError as e:
            if e.is_rate_limit:
                raise RateLimitedError("Rate limit exceeded and retries exhausted") from None
            raise UpstreamUnavailableError(str(e)) from e

        raise UpstreamUnavailableError("Request failed after retries")

    async def _make_request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Make a single HTTP request and handle the response."""
        try:
            response = await self._client.request(method, path, json=json)
        except httpx.RequestError as e:
            raise _RetryableError(f"Network error: {e}") from e

        if response.status_code in (200, 202):
            return response

        if response.status_code in (401, 403):
            raise AuthError(f"Authentication failed: {response.status_code} - {response.text}")

        if response.status_code == 400:
            data = response.json()
            violations = [
                SchemaViolation(path=v.get("path", ""), message=v.get("message", ""))
                for v in data.get("violations", [])
            ]
            raise InvalidInputError(
                data.get("message", "Invalid input"),
                violations=violations,
            )

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            wait_time = float(retry_after) if retry_after else None
            raise _RetryableError("Rate limited", retry_after=wait_time, is_rate_limit=True)

        if response.status_code >= 500:
            raise UpstreamUnavailableError(
                f"Upstream unavailable: {response.status_code} - {response.text}"
            )

        raise UpstreamUnavailableError(
            f"Unexpected response: {response.status_code} - {response.text}"
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> StepsClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
