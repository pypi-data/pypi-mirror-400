from __future__ import annotations

import os
from dataclasses import dataclass

from airops.errors import AiropsError

DEFAULT_API_BASE_URL = "https://api.airops.com"
DEFAULT_TIMEOUT_S = 7200  # 2 hours
DEFAULT_POLL_INTERVAL_S = 2.0


class ConfigError(AiropsError):
    """Configuration error."""

    pass


@dataclass(frozen=True)
class Config:
    """SDK configuration loaded from environment."""

    api_token: str
    api_base_url: str
    default_timeout_s: int
    poll_interval_s: float


_config: Config | None = None


def get_config() -> Config:
    """Get or create the SDK configuration from environment variables.

    Required environment variables:
        AIROPS_API_TOKEN: Bearer token for API authentication

    Optional environment variables:
        AIROPS_API_BASE_URL: Base URL for the Steps API (default: https://api.airops.com)
        AIROPS_DEFAULT_TIMEOUT_S: Default timeout for step execution (default: 7200)
        AIROPS_POLL_INTERVAL_S: Polling interval in seconds (default: 2.0)

    Raises:
        ConfigError: If required configuration is missing.
    """
    global _config

    if _config is not None:
        return _config

    api_token = os.environ.get("AIROPS_API_TOKEN")
    if not api_token:
        raise ConfigError(
            "AIROPS_API_TOKEN environment variable is required. Set it to your AirOps API token."
        )

    api_base_url = os.environ.get("AIROPS_API_BASE_URL", DEFAULT_API_BASE_URL).rstrip("/")

    timeout_str = os.environ.get("AIROPS_DEFAULT_TIMEOUT_S")
    default_timeout_s = int(timeout_str) if timeout_str else DEFAULT_TIMEOUT_S

    poll_str = os.environ.get("AIROPS_POLL_INTERVAL_S")
    poll_interval_s = float(poll_str) if poll_str else DEFAULT_POLL_INTERVAL_S

    _config = Config(
        api_token=api_token,
        api_base_url=api_base_url,
        default_timeout_s=default_timeout_s,
        poll_interval_s=poll_interval_s,
    )

    return _config


def reset_config() -> None:
    """Reset the configuration (useful for testing)."""
    global _config
    _config = None
