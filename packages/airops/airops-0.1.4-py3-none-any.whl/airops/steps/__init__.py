"""AirOps Steps client module.

Usage:
    from airops import steps

    result = await steps.execute("google_search", {"query": "site:example.com"})
"""

from __future__ import annotations

from typing import Any

from airops.steps.client import StepHandle, StepsClient, StepStatus

__all__ = ["execute", "start", "poll", "StepHandle", "StepStatus"]

_client: StepsClient | None = None


def _get_client() -> StepsClient:
    """Get or create the global StepsClient instance."""
    global _client
    if _client is None:
        _client = StepsClient()
    return _client


async def execute(
    step_type: str,
    inputs: dict[str, Any],
    timeout_s: int | None = None,
) -> dict[str, Any]:
    """Execute a step and wait for completion.

    Args:
        step_type: The type of step to execute (e.g., "google_search").
        inputs: Input parameters for the step.
        timeout_s: Maximum time to wait for completion (default: 2 hours).

    Returns:
        The step outputs as a dictionary.

    Example:
        >>> from airops import steps
        >>> result = await steps.execute("google_search", {"query": "airops"})
        >>> print(result["results"])
    """
    return await _get_client().execute(step_type, inputs, timeout_s=timeout_s)


async def start(step_type: str, inputs: dict[str, Any]) -> StepHandle:
    """Start a step execution.

    Args:
        step_type: The type of step to execute.
        inputs: Input parameters for the step.

    Returns:
        A handle containing the step_execution_id for polling.

    Example:
        >>> from airops import steps
        >>> handle = await steps.start("google_search", {"query": "airops"})
        >>> status = await steps.poll(handle.step_execution_id)
    """
    return await _get_client().start(step_type, inputs)


async def poll(step_execution_id: str) -> StepStatus:
    """Poll the status of a step execution.

    Args:
        step_execution_id: The ID of the step execution to poll.

    Returns:
        The current status of the execution.
    """
    return await _get_client().poll(step_execution_id)


async def reset() -> None:
    """Reset the global client (useful for testing)."""
    global _client
    if _client is not None:
        await _client.close()
        _client = None
