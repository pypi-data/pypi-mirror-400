from __future__ import annotations

from dataclasses import dataclass, field


class AiropsError(Exception):
    """Base exception for all AirOps SDK errors."""

    pass


class AuthError(AiropsError):
    """Authentication or authorization failed (401/403)."""

    pass


@dataclass
class SchemaViolation:
    """A single schema validation violation."""

    path: str
    message: str


class InvalidInputError(AiropsError):
    """Input validation failed (400)."""

    violations: list[SchemaViolation] = field(default_factory=list)

    def __init__(self, message: str, violations: list[SchemaViolation] | None = None) -> None:
        super().__init__(message)
        self.violations = violations or []


class RateLimitedError(AiropsError):
    """Rate limit exceeded and retries exhausted (429)."""

    pass


@dataclass
class StepErrorDetails:
    """Details about a step execution error."""

    code: str
    message: str
    details: dict[str, object] | None = None
    retryable: bool = False


class StepFailedError(AiropsError):
    """Step execution failed with status=error."""

    error_details: StepErrorDetails | None = None

    def __init__(self, message: str, error_details: StepErrorDetails | None = None) -> None:
        super().__init__(message)
        self.error_details = error_details


class StepTimeoutError(AiropsError):
    """Step execution polling timed out."""

    pass


class UpstreamUnavailableError(AiropsError):
    """Upstream service unavailable (5xx or network error)."""

    pass
