"""In-memory run store for tracking tool execution state.

This store tracks the state of tool runs using the start/poll pattern:
- POST /runs starts execution in background, returns run_id immediately
- GET /runs/{run_id} polls for status and results
- Store tracks state transitions: queued -> running -> success/error

Note: This is an in-memory implementation for local development (POC).
Production deployments would need shared storage (Redis, database).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from threading import Lock
from typing import Any


class RunStatus(str, Enum):
    """Status of a tool run."""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"


@dataclass
class RunError:
    """Error details for a failed run."""

    code: str
    message: str
    details: dict[str, Any] | None = None


@dataclass
class Run:
    """A tool run record."""

    run_id: str
    status: RunStatus
    created_at: datetime
    updated_at: datetime
    inputs: dict[str, Any]
    outputs: dict[str, Any] | None = None
    error: RunError | None = None


class RunStore:
    """In-memory store for tool runs."""

    def __init__(self) -> None:
        self._runs: dict[str, Run] = {}
        self._lock = Lock()

    def create(self, inputs: dict[str, Any]) -> Run:
        """Create a new run in queued state.

        Args:
            inputs: The tool inputs for this run.

        Returns:
            The created run record.
        """
        run_id = str(uuid.uuid4())
        now = datetime.now(UTC)

        run = Run(
            run_id=run_id,
            status=RunStatus.QUEUED,
            created_at=now,
            updated_at=now,
            inputs=inputs,
        )

        with self._lock:
            self._runs[run_id] = run

        return run

    def get(self, run_id: str) -> Run | None:
        """Get a run by ID.

        Args:
            run_id: The run ID to look up.

        Returns:
            The run record, or None if not found.
        """
        with self._lock:
            return self._runs.get(run_id)

    def set_running(self, run_id: str) -> None:
        """Mark a run as running.

        Args:
            run_id: The run ID to update.
        """
        with self._lock:
            run = self._runs.get(run_id)
            if run:
                run.status = RunStatus.RUNNING
                run.updated_at = datetime.now(UTC)

    def set_success(self, run_id: str, outputs: dict[str, Any]) -> None:
        """Mark a run as successful with outputs.

        Args:
            run_id: The run ID to update.
            outputs: The tool outputs.
        """
        with self._lock:
            run = self._runs.get(run_id)
            if run:
                run.status = RunStatus.SUCCESS
                run.outputs = outputs
                run.updated_at = datetime.now(UTC)

    def set_error(self, run_id: str, error: RunError) -> None:
        """Mark a run as failed with error details.

        Args:
            run_id: The run ID to update.
            error: The error details.
        """
        with self._lock:
            run = self._runs.get(run_id)
            if run:
                run.status = RunStatus.ERROR
                run.error = error
                run.updated_at = datetime.now(UTC)

    def clear(self) -> None:
        """Clear all runs (useful for testing)."""
        with self._lock:
            self._runs.clear()


# Global store instance
_store: RunStore | None = None


def get_store() -> RunStore:
    """Get or create the global run store."""
    global _store
    if _store is None:
        _store = RunStore()
    return _store


def reset_store() -> None:
    """Reset the global store (useful for testing)."""
    global _store
    _store = None
