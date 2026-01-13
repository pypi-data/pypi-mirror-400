"""Tests for error model."""

from __future__ import annotations

from airops.errors import (
    AiropsError,
    AuthError,
    InvalidInputError,
    RateLimitedError,
    SchemaViolation,
    StepErrorDetails,
    StepFailedError,
    StepTimeoutError,
    UpstreamUnavailableError,
)


def test_airops_error_is_base() -> None:
    """All errors inherit from AiropsError."""
    assert issubclass(AuthError, AiropsError)
    assert issubclass(InvalidInputError, AiropsError)
    assert issubclass(RateLimitedError, AiropsError)
    assert issubclass(StepFailedError, AiropsError)
    assert issubclass(StepTimeoutError, AiropsError)
    assert issubclass(UpstreamUnavailableError, AiropsError)


def test_invalid_input_error_with_violations() -> None:
    """InvalidInputError can store schema violations."""
    violations = [
        SchemaViolation(path="/url", message="required field"),
        SchemaViolation(path="/count", message="must be positive"),
    ]
    error = InvalidInputError("Validation failed", violations=violations)

    assert str(error) == "Validation failed"
    assert len(error.violations) == 2
    assert error.violations[0].path == "/url"
    assert error.violations[1].message == "must be positive"


def test_step_failed_error_with_details() -> None:
    """StepFailedError can store error details."""
    details = StepErrorDetails(
        code="TIMEOUT",
        message="Step timed out",
        details={"elapsed": 30},
        retryable=True,
    )
    error = StepFailedError("Step failed", error_details=details)

    assert str(error) == "Step failed"
    assert error.error_details is not None
    assert error.error_details.code == "TIMEOUT"
    assert error.error_details.retryable is True
