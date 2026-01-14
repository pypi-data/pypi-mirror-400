from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any

import httpx

from airops.config import Config
from airops.errors import (
    InvalidInputError,
    SchemaViolation,
    StepErrorDetails,
    StepFailedError,
    StepTimeoutError,
)
from airops.http import BaseClient

logger = logging.getLogger(__name__)

StepResult = dict[str, Any] | list[Any] | str


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


class StepsClient(BaseClient):
    """Client for executing AirOps steps via the Steps API."""

    _success_status_codes = (200, 202)

    def __init__(self, config: Config | None = None) -> None:
        super().__init__(config)

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle 400 InvalidInputError for steps API."""
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

        logger.info(
            "Polling step execution %s (type=%s, timeout=%ds)",
            handle.step_execution_id,
            step_type,
            timeout,
        )

        while True:
            status = await self.poll(handle.step_execution_id)

            if status.status == "success":
                logger.info(
                    "Step execution %s completed successfully",
                    handle.step_execution_id,
                )
                return status.outputs or {}

            if status.status == "error":
                err_msg = status.error.message if status.error else "unknown error"
                logger.info(
                    "Step execution %s failed: %s",
                    handle.step_execution_id,
                    err_msg,
                )
                raise StepFailedError(
                    f"Step '{step_type}' failed: {err_msg}",
                    error_details=status.error,
                )

            if time.monotonic() >= deadline:
                logger.info(
                    "Step execution %s timed out after %ds",
                    handle.step_execution_id,
                    timeout,
                )
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
        logger.info("Starting step execution (type=%s)", step_type)
        response = await self._request_with_retry(
            "POST",
            "/internal_api/steps/executions",
            json={"type": step_type, "inputs": inputs},
        )

        data = response.json()
        handle = StepHandle(step_execution_id=data["step_execution_id"])
        logger.info("Step execution started: %s", handle.step_execution_id)
        return handle

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
