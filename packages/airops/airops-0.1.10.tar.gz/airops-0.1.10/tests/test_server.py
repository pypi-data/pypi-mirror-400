"""Tests for server routes."""

from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient
from pydantic import Field

from airops import Tool, ToolOutputs
from airops.inputs import MultiSelect, ShortText, SingleSelect, ToolInputs


class EchoInputs(ToolInputs):
    message: ShortText = Field(..., description="Message to echo")


class EchoOutputs(ToolOutputs):
    echo: str


@pytest.fixture
def echo_tool() -> Tool:
    """Create a simple echo tool for testing."""
    tool = Tool(
        name="echo_tool",
        description="Echoes the input message",
        input_model=EchoInputs,
        output_model=EchoOutputs,
    )

    @tool.handler
    async def run(inputs: EchoInputs) -> EchoOutputs:
        return EchoOutputs(echo=inputs.message)

    return tool


@pytest.fixture
def client(echo_tool: Tool) -> TestClient:
    """Create test client for echo tool."""
    return TestClient(echo_tool.app)


def test_health_endpoint(client: TestClient) -> None:
    """Health endpoint returns ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_start_run(client: TestClient) -> None:
    """POST /runs starts a run."""
    response = client.post(
        "/runs",
        json={"inputs": {"message": "hello"}},
    )
    assert response.status_code == 202

    data = response.json()
    assert "run_id" in data
    assert data["status"] == "queued"


def test_get_run_not_found(client: TestClient) -> None:
    """GET /runs/{run_id} returns 404 for unknown run."""
    response = client.get("/runs/nonexistent")
    assert response.status_code == 404


def test_run_lifecycle(client: TestClient) -> None:
    """Full run lifecycle: start -> poll -> success."""
    # Start run
    start_response = client.post(
        "/runs",
        json={"inputs": {"message": "test message"}},
    )
    assert start_response.status_code == 202
    run_id = start_response.json()["run_id"]

    # Poll until complete (with timeout)
    deadline = time.time() + 5
    while time.time() < deadline:
        poll_response = client.get(f"/runs/{run_id}")
        assert poll_response.status_code == 200

        data = poll_response.json()
        if data["status"] == "success":
            assert data["outputs"] == {"echo": "test message"}
            return

        time.sleep(0.1)

    pytest.fail("Run did not complete in time")


def test_invalid_inputs(client: TestClient) -> None:
    """Invalid inputs return 400."""
    response = client.post(
        "/runs",
        json={"inputs": {}},  # missing required 'message'
    )
    assert response.status_code == 400


def test_ui_endpoint(client: TestClient) -> None:
    """UI endpoint returns HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "echo_tool" in response.text


def test_error_includes_traceback() -> None:
    """Error response includes full traceback."""
    from airops.server.app import create_app
    from airops.server.store import RunStore

    class FailingInputs(ToolInputs):
        value: ShortText = Field(..., description="A value")

    class FailingOutputs(ToolOutputs):
        result: str

    async def failing_handler(inputs: FailingInputs) -> FailingOutputs:
        # This will raise TypeError with a traceback
        data = [1, 2, 3]
        _ = data["bad"]  # type: ignore[index]
        return FailingOutputs(result="never reached")

    store = RunStore()
    app = create_app(
        tool_name="failing_tool",
        tool_description="A tool that fails",
        handler=failing_handler,
        input_model=FailingInputs,
        output_model=FailingOutputs,
        store=store,
    )

    client = TestClient(app)

    # Start run
    start_response = client.post("/runs", json={"inputs": {"value": "test"}})
    assert start_response.status_code == 202
    run_id = start_response.json()["run_id"]

    # Poll until error
    deadline = time.time() + 5
    while time.time() < deadline:
        poll_response = client.get(f"/runs/{run_id}")
        assert poll_response.status_code == 200

        data = poll_response.json()
        if data["status"] == "error":
            assert data["error"]["message"] == "list indices must be integers or slices, not str"
            assert data["error"]["traceback"] is not None
            assert "Traceback (most recent call last)" in data["error"]["traceback"]
            assert "failing_handler" in data["error"]["traceback"]
            return

        time.sleep(0.1)

    pytest.fail("Run did not complete in time")


def test_refresh_button_navigates_to_run_page() -> None:
    """Refresh button uses GoToEvent to navigate back to run page."""
    from airops.server.app import create_app
    from airops.server.store import RunStore

    async def dummy_handler(inputs: EchoInputs) -> EchoOutputs:
        return EchoOutputs(echo=inputs.message)

    store = RunStore()
    app = create_app(
        tool_name="test_tool",
        tool_description="Test",
        handler=dummy_handler,
        input_model=EchoInputs,
        output_model=EchoOutputs,
        store=store,
    )

    # Create a run directly in running state
    run = store.create({"message": "test"})
    store.set_running(run.run_id)

    client = TestClient(app)
    response = client.get(f"/api/run/{run.run_id}")
    assert response.status_code == 200

    data = response.json()
    response_str = str(data)

    # Verify running state shows refresh button with GoToEvent (serialized as 'go-to')
    assert "running" in response_str
    assert "'type': 'go-to'" in response_str
    assert f"/run/{run.run_id}" in response_str


def test_ui_renders_single_select_as_dropdown() -> None:
    """SingleSelect fields render as FormFieldSelect."""
    from airops.server.app import create_app
    from airops.server.store import RunStore

    class SelectInputs(ToolInputs):
        format: SingleSelect("json", "csv", "xml") = Field(default="json")

    class SelectOutputs(ToolOutputs):
        result: str

    async def handler(inputs: SelectInputs) -> SelectOutputs:
        return SelectOutputs(result=inputs.format)

    store = RunStore()
    app = create_app(
        tool_name="select_tool",
        tool_description="Test select",
        handler=handler,
        input_model=SelectInputs,
        output_model=SelectOutputs,
        store=store,
    )

    client = TestClient(app)
    response = client.get("/api/")
    assert response.status_code == 200

    data = response.json()
    form = data[0]["components"][2]

    assert form["type"] == "Form"
    fields = form["formFields"]
    assert len(fields) == 1

    select_field = fields[0]
    assert select_field["type"] == "FormFieldSelect"
    assert select_field["name"] == "format"
    assert select_field.get("multiple") is None  # Not present or None for single select
    assert select_field["options"] == [
        {"value": "json", "label": "json"},
        {"value": "csv", "label": "csv"},
        {"value": "xml", "label": "xml"},
    ]


def test_ui_renders_multi_select_as_multi_dropdown() -> None:
    """MultiSelect fields render as FormFieldSelect with multiple=True."""
    from airops.server.app import create_app
    from airops.server.store import RunStore

    class TagInputs(ToolInputs):
        tags: MultiSelect("urgent", "important", "low") = Field(default=[])

    class TagOutputs(ToolOutputs):
        result: list[str]

    async def handler(inputs: TagInputs) -> TagOutputs:
        return TagOutputs(result=inputs.tags)

    store = RunStore()
    app = create_app(
        tool_name="tag_tool",
        tool_description="Test multi select",
        handler=handler,
        input_model=TagInputs,
        output_model=TagOutputs,
        store=store,
    )

    client = TestClient(app)
    response = client.get("/api/")
    assert response.status_code == 200

    data = response.json()
    form = data[0]["components"][2]

    assert form["type"] == "Form"
    fields = form["formFields"]
    assert len(fields) == 1

    select_field = fields[0]
    assert select_field["type"] == "FormFieldSelect"
    assert select_field["name"] == "tags"
    assert select_field["multiple"] is True
    assert select_field["options"] == [
        {"value": "urgent", "label": "urgent"},
        {"value": "important", "label": "important"},
        {"value": "low", "label": "low"},
    ]
