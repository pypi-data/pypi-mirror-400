"""Template strings for airops init scaffolding."""

from __future__ import annotations

DOCKERFILE_TEMPLATE = """\
FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files and install
COPY pyproject.toml ./
RUN uv sync --no-dev --no-install-project

# Copy application code and environment
COPY tool.py .env ./

# Expose port for AWS App Runner
EXPOSE 8080

# Run the tool server
CMD ["uv", "run", "python", "tool.py"]
"""

DOCKERIGNORE_TEMPLATE = """\
.venv/
__pycache__/
*.pyc
.pytest_cache/
.mypy_cache/
.ruff_cache/
tests/
README.md
"""

TOOL_TEMPLATE = '''\
"""AirOps Tool: {name}"""

import os

from pydantic import Field

from airops import Tool, ToolOutputs, steps
from airops.inputs import Number, ShortText, ToolInputs


class Inputs(ToolInputs):
    """Tool input parameters."""

    query: ShortText = Field(..., description="Search query")
    limit: Number = Field(default=10, description="Maximum results")


class Outputs(ToolOutputs):
    """Tool output values."""

    results: list[dict]


tool = Tool(
    name="{name}",
    description="Description of what this tool does",
    input_model=Inputs,
    output_model=Outputs,
)


@tool.handler
async def run(inputs: Inputs) -> Outputs:
    """Execute the tool logic.

    Args:
        inputs: Validated input parameters.

    Returns:
        Tool outputs.
    """
    # Example: Call an AirOps step
    # response = await steps.execute("google_search", {{"query": inputs.query}})
    # return Outputs(results=response["results"])

    # Placeholder implementation
    return Outputs(results=[{{"query": inputs.query, "message": "Hello from {name}!"}}])


if __name__ == "__main__":
    reload = os.environ.get("HOT_RELOAD", "").lower() in ("1", "true")
    tool.serve(reload=reload)
'''

ENV_EXAMPLE_TEMPLATE = """\
# AirOps API Configuration
# Copy this file to .env and fill in your values

# Required: Your AirOps API token
AIROPS_API_TOKEN=your-api-token-here

# Optional: API base URL (defaults to https://api.airops.com)
# AIROPS_API_BASE_URL=https://api.airops.com

# Optional: Default timeout for step execution in seconds (defaults to 7200)
# AIROPS_DEFAULT_TIMEOUT_S=7200

# Optional: Polling interval in seconds (defaults to 2.0)
# AIROPS_POLL_INTERVAL_S=2.0
"""

PYPROJECT_TEMPLATE = """\
[project]
name = "{name}"
version = "0.1.0"
description = "An AirOps tool"
requires-python = ">=3.13"
dependencies = [
    "airops>=0.1.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
"""

README_TEMPLATE = """\
# {name}

An AirOps tool.

## Quick Start

1. Configure environment:

```bash
cp .env.example .env
# Edit .env and add your AIROPS_API_TOKEN
```

2. Run with hot reload:

```bash
airops run
```

This starts:
- **API**: http://localhost:8080/runs
- **UI**: http://localhost:8080/

## Testing

```bash
uv sync
uv run pytest tests/ -v
```

## Usage

### Start a run

```bash
curl -X POST http://localhost:8080/runs \\
  -H "Content-Type: application/json" \\
  -d '{{"inputs": {{"query": "example"}}}}'
```

### Poll for results

```bash
curl http://localhost:8080/runs/<run_id>
```

## Production

Run without hot-reload:

```bash
docker run -p 8080:8080 {name}
```
"""

TEST_TOOL_TEMPLATE = '''\
"""Tests for {name} tool."""

from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient

from tool import Inputs, Outputs, tool


@pytest.fixture
def client() -> TestClient:
    """Create test client for the tool."""
    return TestClient(tool.app)


def test_health_endpoint(client: TestClient) -> None:
    """Health endpoint returns ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {{"status": "ok"}}


def test_start_run(client: TestClient) -> None:
    """POST /runs starts a run."""
    response = client.post(
        "/runs",
        json={{"inputs": {{"query": "test", "limit": 5}}}},
    )
    assert response.status_code == 202
    data = response.json()
    assert "run_id" in data
    assert data["status"] == "queued"


def test_run_completes(client: TestClient) -> None:
    """Run completes successfully."""
    # Start run
    response = client.post(
        "/runs",
        json={{"inputs": {{"query": "hello"}}}},
    )
    assert response.status_code == 202
    run_id = response.json()["run_id"]

    # Poll until complete
    deadline = time.time() + 5
    while time.time() < deadline:
        poll = client.get(f"/runs/{{run_id}}")
        assert poll.status_code == 200
        data = poll.json()
        if data["status"] == "success":
            assert "results" in data["outputs"]
            return
        time.sleep(0.1)

    pytest.fail("Run did not complete in time")


def test_invalid_inputs(client: TestClient) -> None:
    """Invalid inputs return 400."""
    response = client.post(
        "/runs",
        json={{"inputs": {{}}}},  # missing required 'query'
    )
    assert response.status_code == 400
'''
