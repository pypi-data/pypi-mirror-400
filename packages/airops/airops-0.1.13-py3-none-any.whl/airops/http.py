"""Base HTTP client with retry logic for AirOps API clients."""

from __future__ import annotations

from typing import Any, Self

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
    RateLimitedError,
    UpstreamUnavailableError,
)


class RetryableError(Exception):
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
    if isinstance(exc, RetryableError) and exc.retry_after is not None:
        return exc.retry_after
    return wait_exponential_jitter(initial=1, max=60)(retry_state)


class BaseClient:
    """Base HTTP client with retry logic for AirOps APIs."""

    _success_status_codes: tuple[int, ...] = (200,)

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
            RateLimitedError: If rate limits are exhausted.
            UpstreamUnavailableError: If the API is unavailable.
        """
        try:
            async for attempt in AsyncRetrying(
                retry=retry_if_exception_type(RetryableError),
                stop=stop_after_attempt(max_retries + 1),
                wait=_wait_with_retry_after,
                reraise=True,
            ):
                with attempt:
                    return await self._make_request(method, path, json=json)
        except RetryableError as e:
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
            raise RetryableError(f"Network error: {e}") from e

        if response.status_code in self._success_status_codes:
            return response

        if response.status_code in (401, 403):
            raise AuthError(f"Authentication failed: {response.status_code} - {response.text}")

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            wait_time = float(retry_after) if retry_after else None
            raise RetryableError("Rate limited", retry_after=wait_time, is_rate_limit=True)

        # Allow subclasses to handle specific status codes
        self._handle_error_response(response)

        if response.status_code >= 500:
            raise UpstreamUnavailableError(
                f"Upstream unavailable: {response.status_code} - {response.text}"
            )

        raise UpstreamUnavailableError(
            f"Unexpected response: {response.status_code} - {response.text}"
        )

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle client-specific error responses.

        Subclasses can override this to handle specific status codes.
        Should raise an appropriate exception or return to fall through
        to default error handling.
        """
        pass

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
