# Building an AirOps Tool: Step-by-Step Instructions

This guide walks you through building a custom AirOps tool using the Python SDK. By the end, you'll have a working tool that can be deployed to the AirOps platform.

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Installation](#2-installation)
3. [Project Setup](#3-project-setup)
4. [Understanding the Tool Structure](#4-understanding-the-tool-structure)
5. [Defining Input and Output Models](#5-defining-input-and-output-models)
6. [Writing the Handler Function](#6-writing-the-handler-function)
7. [Using the Steps API](#7-using-the-steps-api)
8. [Error Handling](#8-error-handling)
9. [Running Locally](#9-running-locally)
10. [Testing Your Tool](#10-testing-your-tool)
11. [Configuration Reference](#11-configuration-reference)
12. [Deployment](#12-deployment)
13. [Advanced Patterns](#13-advanced-patterns)

---

## 1. Prerequisites

Before you begin, ensure you have:

- **Python 3.13 or later** installed
- **uv** package manager (recommended for this project)
- An **AirOps API token** (obtain from the AirOps platform)

To install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 2. Installation

Install the AirOps SDK:

```bash
pip install airops
```

Or with uv:

```bash
uv add airops
```

---

## 3. Project Setup

### Option A: Use the CLI Scaffolding (Recommended)

The fastest way to start is using the built-in project generator:

```bash
airops init my-tool
cd my-tool
```

This creates a complete project structure:

```
my-tool/
├── tool.py           # Your tool implementation
├── pyproject.toml    # Python package configuration
├── Dockerfile        # Container image for deployment
├── .env.example      # Environment variable template
├── tests/
│   └── test_tool.py  # Example tests
└── README.md         # Documentation
```

### Option B: Manual Setup

Create a new directory and set up the files yourself:

```bash
mkdir my-tool && cd my-tool
```

Create `pyproject.toml`:

```toml
[project]
name = "my-tool"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = ["airops"]

[project.optional-dependencies]
dev = ["pytest", "pytest-asyncio"]
```

Create `tool.py`:

```python
from pydantic import Field
from airops import Tool, ToolOutputs
from airops.inputs import ToolInputs, ShortText

class Inputs(ToolInputs):
    message: ShortText = Field(..., description="Input message")

class Outputs(ToolOutputs):
    result: str

tool = Tool(
    name="my_tool",
    description="A simple example tool",
    input_model=Inputs,
    output_model=Outputs,
)

@tool.handler
async def run(inputs: Inputs) -> Outputs:
    return Outputs(result=f"Processed: {inputs.message}")

if __name__ == "__main__":
    tool.serve()
```

### Configure Environment Variables

Copy the example environment file and add your API token:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
AIROPS_API_TOKEN=your-api-token-here
```

---

## 4. Understanding the Tool Structure

An AirOps tool consists of three main components:

### 4.1 The Tool Instance

```python
from airops import Tool

tool = Tool(
    name="my_tool",           # Unique identifier (snake_case)
    description="Description", # Human-readable description
    input_model=Inputs,       # ToolInputs subclass for inputs
    output_model=Outputs,     # ToolOutputs subclass for outputs
)
```

The `Tool` class:
- Validates inputs and outputs using Pydantic models
- Creates a FastAPI application with REST endpoints
- Provides a web UI for testing
- Handles hot-reload during development
- Generates AirOps workflow-compatible input schemas

### 4.2 Input/Output Models

Input models must inherit from `ToolInputs` and use AirOps input types. Output models must inherit from `ToolOutputs`:

```python
from pydantic import Field
from airops import ToolOutputs
from airops.inputs import ToolInputs, ShortText, Number

class Inputs(ToolInputs):
    query: ShortText = Field(..., description="Search query")
    limit: Number = Field(default=10, description="Max results")

class Outputs(ToolOutputs):
    results: list[dict]
    total_count: int
```

### 4.3 The Handler Function

The async handler processes inputs and returns outputs:

```python
@tool.handler
async def run(inputs: Inputs) -> Outputs:
    # Your logic here
    return Outputs(results=[], total_count=0)
```

---

## 5. Defining Input and Output Models

### AirOps Input Types

The SDK provides specialized input types that map to AirOps workflow UI components:

```python
from pydantic import Field
from airops.inputs import (
    ToolInputs,
    ShortText,      # Single-line text input
    LongText,       # Multi-line text input
    Number,         # Numeric input (int or float)
    Json,           # JSON data input
    SingleSelect,   # Dropdown with single selection
    MultiSelect,    # Dropdown with multiple selections
    KnowledgeBase,  # AirOps knowledge base reference (int ID)
    Brandkit,       # AirOps brandkit reference (int ID)
    Database,       # AirOps database reference (int ID)
)

class Inputs(ToolInputs):
    # Required text field
    query: ShortText = Field(..., description="Search query")

    # Optional field with default
    limit: Number = Field(default=10, description="Number of results")

    # Long text for multi-line content
    content: LongText = Field(..., description="Article content")

    # JSON data
    config: Json = Field(default={}, description="Configuration options")

    # Single selection from options
    format: SingleSelect("json", "csv", "xml") = Field(default="json")

    # Multiple selections from options
    tags: MultiSelect("urgent", "important", "low") = Field(default=[])

    # AirOps resource references
    kb_id: KnowledgeBase = Field(..., description="Knowledge base to search")
    brand_id: Brandkit = Field(..., description="Brand guidelines to use")
    db_id: Database = Field(..., description="Database to query")
```

### Output Models

Output models inherit from `ToolOutputs` and use standard Python types (must be JSON serializable):

```python
from pydantic import BaseModel
from airops import ToolOutputs

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    score: float

class Outputs(ToolOutputs):
    results: list[SearchResult]
    total_count: int
    query_time_ms: float
    metadata: dict[str, str]
```

### Field Descriptions Matter

Field descriptions are displayed in the web UI and become the `hint` in the AirOps workflow builder:

```python
class Inputs(ToolInputs):
    url: ShortText = Field(
        ...,
        description="Full URL to analyze (must include https://)"
    )
    depth: Number = Field(
        default=1,
        description="How many levels deep to crawl (1-5)"
    )
```

---

## 6. Writing the Handler Function

### Basic Handler

```python
@tool.handler
async def run(inputs: Inputs) -> Outputs:
    # Process the inputs
    processed = inputs.query.upper()

    # Return outputs matching the model
    return Outputs(result=processed)
```

### Handler with External API Calls

```python
import httpx

@tool.handler
async def run(inputs: Inputs) -> Outputs:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.example.com/search",
            params={"q": inputs.query}
        )
        response.raise_for_status()
        data = response.json()

    return Outputs(
        results=data["items"],
        total_count=data["total"]
    )
```

### Handler with Multiple Operations

```python
@tool.handler
async def run(inputs: Inputs) -> Outputs:
    # Step 1: Fetch data
    raw_data = await fetch_data(inputs.url)

    # Step 2: Process data
    processed = process_data(raw_data)

    # Step 3: Enrich with additional info
    enriched = await enrich_data(processed)

    return Outputs(
        data=enriched,
        source_url=inputs.url,
        processed_at=datetime.now().isoformat()
    )
```

---

## 7. Using the Steps API

The Steps API lets you call pre-built AirOps steps from within your tool.

### Simple Execution

```python
from airops import steps

@tool.handler
async def run(inputs: Inputs) -> Outputs:
    # Execute a step and wait for results
    result = await steps.execute(
        "google_search",
        {"query": inputs.query, "limit": inputs.limit}
    )

    return Outputs(results=result["results"])
```

### Execution with Custom Timeout

```python
result = await steps.execute(
    "long_running_step",
    {"data": inputs.data},
    timeout_s=600  # 10 minutes
)
```

### Manual Step Control

For more control over step execution:

```python
from airops import steps

@tool.handler
async def run(inputs: Inputs) -> Outputs:
    # Start the step (non-blocking)
    handle = await steps.start("google_search", {"query": inputs.query})

    # Do other work while step runs...
    other_data = await fetch_other_data()

    # Poll for completion
    status = await steps.poll(handle.step_execution_id)

    while status.status not in ("success", "error"):
        await asyncio.sleep(1)
        status = await steps.poll(handle.step_execution_id)

    if status.status == "error":
        raise Exception(f"Step failed: {status.error.message}")

    return Outputs(
        search_results=status.outputs["results"],
        other_data=other_data
    )
```

### Parallel Step Execution

Execute multiple steps concurrently:

```python
import asyncio
from airops import steps

@tool.handler
async def run(inputs: Inputs) -> Outputs:
    # Start multiple steps in parallel
    results = await asyncio.gather(
        steps.execute("google_search", {"query": inputs.query}),
        steps.execute("bing_search", {"query": inputs.query}),
        steps.execute("duckduckgo_search", {"query": inputs.query}),
    )

    google_results, bing_results, ddg_results = results

    # Combine results
    all_results = (
        google_results["results"] +
        bing_results["results"] +
        ddg_results["results"]
    )

    return Outputs(results=all_results)
```

### Using the Steps Client Directly

For advanced use cases:

```python
from airops.steps.client import StepsClient

@tool.handler
async def run(inputs: Inputs) -> Outputs:
    client = StepsClient()
    try:
        handle = await client.start("google_search", {"query": inputs.query})

        # Custom polling logic
        for _ in range(60):
            status = await client.poll(handle.step_execution_id)
            if status.status == "success":
                return Outputs(results=status.outputs["results"])
            elif status.status == "error":
                break
            await asyncio.sleep(2)

        raise TimeoutError("Step did not complete in time")
    finally:
        await client.close()
```

---

## 8. Error Handling

### Exception Hierarchy

The SDK provides specific exceptions for different error scenarios:

```python
from airops.errors import (
    AiropsError,              # Base exception for all SDK errors
    AuthError,                # Authentication failed (401/403)
    InvalidInputError,        # Input validation failed (400)
    RateLimitedError,         # Rate limit exceeded after retries
    StepFailedError,          # Step execution failed
    StepTimeoutError,         # Step didn't complete in time
    UpstreamUnavailableError, # Server errors (5xx) or network issues
)
```

### Basic Error Handling

```python
from airops import steps
from airops.errors import StepFailedError, StepTimeoutError

@tool.handler
async def run(inputs: Inputs) -> Outputs:
    try:
        result = await steps.execute("google_search", {"query": inputs.query})
        return Outputs(results=result["results"], error=None)

    except StepTimeoutError:
        return Outputs(results=[], error="Search timed out")

    except StepFailedError as e:
        return Outputs(results=[], error=f"Search failed: {e.error_details.message}")
```

### Comprehensive Error Handling

```python
from airops import steps
from airops.errors import (
    AuthError,
    InvalidInputError,
    RateLimitedError,
    StepFailedError,
    StepTimeoutError,
    UpstreamUnavailableError,
)

@tool.handler
async def run(inputs: Inputs) -> Outputs:
    try:
        result = await steps.execute("google_search", {"query": inputs.query})
        return Outputs(results=result["results"])

    except AuthError:
        # API token is invalid or expired
        raise RuntimeError("Authentication failed - check AIROPS_API_TOKEN")

    except InvalidInputError as e:
        # Input validation failed
        messages = [f"{v.path}: {v.message}" for v in e.violations]
        raise ValueError(f"Invalid inputs: {', '.join(messages)}")

    except RateLimitedError:
        # Rate limit exceeded even after retries
        raise RuntimeError("Rate limited - try again later")

    except StepTimeoutError:
        # Step didn't complete within timeout
        return Outputs(results=[], error="Operation timed out")

    except StepFailedError as e:
        # Step failed during execution
        if e.error_details and e.error_details.retryable:
            # Could implement retry logic here
            pass
        return Outputs(results=[], error=e.error_details.message)

    except UpstreamUnavailableError:
        # AirOps API is down or unreachable
        raise RuntimeError("AirOps service unavailable")
```

### Accessing Error Details

```python
except StepFailedError as e:
    if e.error_details:
        print(f"Error message: {e.error_details.message}")
        print(f"Error code: {e.error_details.code}")
        print(f"Is retryable: {e.error_details.retryable}")

except InvalidInputError as e:
    for violation in e.violations:
        print(f"Field: {violation.path}")
        print(f"Error: {violation.message}")
```

---

## 9. Running Locally

### Using the CLI

The recommended way to run your tool during development:

```bash
airops run
```

This:
- Starts the server at `http://localhost:8080`
- Enables hot-reload (code changes auto-restart the server)
- Serves the web UI at the root URL

### Using Python Directly

```bash
python tool.py
```

Or with uv:

```bash
uv run python tool.py
```

### Custom Host and Port

```python
if __name__ == "__main__":
    tool.serve(
        host="0.0.0.0",  # Listen on all interfaces
        port=9000,        # Custom port
        ui=True,          # Enable web UI (default)
        reload=True,      # Enable hot reload
    )
```

### Accessing the Tool

Once running, you can access:

- **Web UI**: `http://localhost:8080/` - Form-based interface for testing
- **API**: `http://localhost:8080/runs` - REST API endpoints
- **Health**: `http://localhost:8080/health` - Health check endpoint

### API Usage

Start a run:

```bash
curl -X POST http://localhost:8080/runs \
  -H "Content-Type: application/json" \
  -d '{"inputs": {"query": "test"}}'
```

Response:

```json
{
  "run_id": "abc123",
  "status": "queued"
}
```

Poll for results:

```bash
curl http://localhost:8080/runs/abc123
```

Response:

```json
{
  "run_id": "abc123",
  "status": "success",
  "outputs": {"results": [...]},
  "created_at": "2024-01-15T10:30:00Z",
  "started_at": "2024-01-15T10:30:01Z",
  "completed_at": "2024-01-15T10:30:05Z"
}
```

---

## 10. Testing Your Tool

### Setting Up Tests

Create `tests/test_tool.py`:

```python
import pytest
from fastapi.testclient import TestClient
from tool import tool, Inputs, Outputs

@pytest.fixture
def client():
    return TestClient(tool.app)
```

### Testing the Handler Directly

```python
import pytest
from tool import tool, Inputs, Outputs

@pytest.mark.asyncio
async def test_handler_directly():
    inputs = Inputs(query="test query", limit=5)
    outputs = await tool._handler(inputs)

    assert isinstance(outputs, Outputs)
    assert len(outputs.results) > 0
```

### Testing via HTTP API

```python
import time

def test_run_execution(client):
    # Start a run
    response = client.post(
        "/runs",
        json={"inputs": {"query": "test"}}
    )
    assert response.status_code == 202

    run_id = response.json()["run_id"]
    assert response.json()["status"] == "queued"

    # Poll until complete
    deadline = time.time() + 10
    while time.time() < deadline:
        poll_response = client.get(f"/runs/{run_id}")
        status = poll_response.json()["status"]

        if status == "success":
            outputs = poll_response.json()["outputs"]
            assert "results" in outputs
            return
        elif status == "error":
            pytest.fail(f"Run failed: {poll_response.json()['error']}")

        time.sleep(0.1)

    pytest.fail("Run did not complete in time")
```

### Testing Input Validation

```python
def test_invalid_input(client):
    response = client.post(
        "/runs",
        json={"inputs": {"invalid_field": "value"}}
    )
    assert response.status_code == 422  # Validation error
```

### Testing Error Cases

```python
def test_missing_required_field(client):
    response = client.post(
        "/runs",
        json={"inputs": {}}  # Missing required 'query' field
    )
    assert response.status_code == 422
    assert "query" in response.text.lower()
```

### Mocking the Steps API

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_with_mocked_steps():
    mock_result = {"results": [{"title": "Test", "url": "http://test.com"}]}

    with patch("airops.steps.execute", new_callable=AsyncMock) as mock_execute:
        mock_execute.return_value = mock_result

        inputs = Inputs(query="test")
        outputs = await tool._handler(inputs)

        mock_execute.assert_called_once_with(
            "google_search",
            {"query": "test"}
        )
        assert outputs.results == mock_result["results"]
```

### Running Tests

```bash
# Run all tests
uv run python -m pytest tests/ -v

# Run specific test file
uv run python -m pytest tests/test_tool.py -v

# Run with coverage
uv run python -m pytest tests/ -v --cov=tool
```

---

## 11. Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AIROPS_API_TOKEN` | Yes | - | Your AirOps API token |
| `AIROPS_API_BASE_URL` | No | `https://api.airops.com` | API base URL |
| `AIROPS_DEFAULT_TIMEOUT_S` | No | `7200` | Default step timeout (2 hours) |
| `AIROPS_POLL_INTERVAL_S` | No | `2.0` | Polling interval for step status |
| `HOT_RELOAD` | No | `false` | Enable hot reload in development |
| `WATCHFILES_FORCE_POLLING` | No | `false` | Force polling for file changes (Docker) |

### Accessing Configuration

```python
from airops.config import get_config

config = get_config()
print(config.api_token)
print(config.api_base_url)
print(config.default_timeout_s)
print(config.poll_interval_s)
```

### Tool.serve() Parameters

```python
tool.serve(
    host="0.0.0.0",      # Network interface to bind to
    port=8080,           # Port number
    ui=True,             # Enable/disable web UI
    reload=True,         # Enable hot reload (auto-detected from __main__)
)
```

---

## 12. Deployment

### Using Docker

The scaffolded project includes a Dockerfile:

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir .

EXPOSE 8080

CMD ["python", "tool.py"]
```

Build and run:

```bash
docker build -t my-tool .
docker run -p 8080:8080 -e AIROPS_API_TOKEN=xxx my-tool
```

### Production Considerations

1. **State Storage**: The default `RunStore` is in-memory and only suitable for development. Production deployments need a shared store (Redis, database).

2. **Scaling**: Each instance maintains its own run store. Use external storage for multi-instance deployments.

3. **Health Checks**: Use the `/health` endpoint for container orchestration:
   ```yaml
   healthcheck:
     test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
     interval: 30s
     timeout: 10s
     retries: 3
   ```

4. **Logging**: Add structured logging:
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)

   @tool.handler
   async def run(inputs: Inputs) -> Outputs:
       logger.info(f"Processing query: {inputs.query}")
       # ...
   ```

---

## 13. Advanced Patterns

### Pattern 1: Retry with Backoff

```python
import asyncio
from airops import steps
from airops.errors import StepFailedError

async def execute_with_retry(step_type: str, inputs: dict, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return await steps.execute(step_type, inputs)
        except StepFailedError as e:
            if not e.error_details or not e.error_details.retryable:
                raise
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### Pattern 2: Parallel Processing with Concurrency Limit

```python
import asyncio
from airops import steps

async def process_batch(items: list[str], concurrency: int = 5):
    semaphore = asyncio.Semaphore(concurrency)

    async def process_one(item: str):
        async with semaphore:
            return await steps.execute("process_item", {"item": item})

    return await asyncio.gather(*[process_one(item) for item in items])
```

### Pattern 3: Streaming Results

```python
from typing import AsyncIterator

async def stream_results(query: str) -> AsyncIterator[dict]:
    page = 1
    while True:
        result = await steps.execute(
            "paginated_search",
            {"query": query, "page": page}
        )

        if not result["results"]:
            break

        for item in result["results"]:
            yield item

        page += 1
```

### Pattern 4: Caching Results

```python
from functools import lru_cache
from datetime import datetime, timedelta

_cache = {}
_cache_ttl = timedelta(minutes=5)

async def cached_execute(step_type: str, inputs: dict):
    cache_key = f"{step_type}:{hash(frozenset(inputs.items()))}"

    if cache_key in _cache:
        result, timestamp = _cache[cache_key]
        if datetime.now() - timestamp < _cache_ttl:
            return result

    result = await steps.execute(step_type, inputs)
    _cache[cache_key] = (result, datetime.now())
    return result
```

### Pattern 5: Input Preprocessing

```python
from pydantic import field_validator, Field
from airops.inputs import ToolInputs, ShortText

class Inputs(ToolInputs):
    url: ShortText = Field(..., description="URL to process")

    @field_validator("url")
    @classmethod
    def normalize_url(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith(("http://", "https://")):
            v = f"https://{v}"
        return v
```

### Pattern 6: Conditional Step Execution

```python
import asyncio
from airops import steps

@tool.handler
async def run(inputs: Inputs) -> Outputs:
    # Choose step based on input
    if inputs.source == "google":
        result = await steps.execute("google_search", {"query": inputs.query})
    elif inputs.source == "bing":
        result = await steps.execute("bing_search", {"query": inputs.query})
    else:
        # Run both and merge
        google, bing = await asyncio.gather(
            steps.execute("google_search", {"query": inputs.query}),
            steps.execute("bing_search", {"query": inputs.query}),
        )
        result = {"results": google["results"] + bing["results"]}

    return Outputs(results=result["results"])
```

### Pattern 7: Graceful Degradation

```python
from airops import steps
from airops.errors import StepFailedError, StepTimeoutError

@tool.handler
async def run(inputs: Inputs) -> Outputs:
    results = []
    errors = []

    # Try primary source
    try:
        primary = await steps.execute("primary_search", {"query": inputs.query})
        results.extend(primary["results"])
    except (StepFailedError, StepTimeoutError) as e:
        errors.append(f"Primary search failed: {e}")

    # Try backup source if primary failed or returned few results
    if len(results) < 5:
        try:
            backup = await steps.execute("backup_search", {"query": inputs.query})
            results.extend(backup["results"])
        except (StepFailedError, StepTimeoutError) as e:
            errors.append(f"Backup search failed: {e}")

    return Outputs(
        results=results,
        warnings=errors if errors else None
    )
```

---

## Quick Reference

### Minimal Working Tool

```python
from pydantic import Field
from airops import Tool, ToolOutputs
from airops.inputs import ToolInputs, ShortText

class Inputs(ToolInputs):
    message: ShortText = Field(..., description="Input message")

class Outputs(ToolOutputs):
    result: str

tool = Tool(
    name="echo",
    description="Echoes the input",
    input_model=Inputs,
    output_model=Outputs,
)

@tool.handler
async def run(inputs: Inputs) -> Outputs:
    return Outputs(result=inputs.message)

if __name__ == "__main__":
    tool.serve()
```

### Tool with Steps API

```python
from pydantic import Field
from airops import Tool, ToolOutputs, steps
from airops.inputs import ToolInputs, ShortText

class Inputs(ToolInputs):
    query: ShortText = Field(..., description="Search query")

class Outputs(ToolOutputs):
    results: list[dict]

tool = Tool(
    name="searcher",
    description="Search the web",
    input_model=Inputs,
    output_model=Outputs,
)

@tool.handler
async def run(inputs: Inputs) -> Outputs:
    result = await steps.execute("google_search", {"query": inputs.query})
    return Outputs(results=result["results"])

if __name__ == "__main__":
    tool.serve()
```

### Run Commands

```bash
# Initialize project
airops init my-tool

# Run with hot reload
airops run

# Run tests
uv run python -m pytest tests/ -v

# Run linter
uv run python -m ruff check src/ tests/

# Format code
uv run python -m ruff format src/ tests/

# Type check
uv run python -m mypy src/
```
