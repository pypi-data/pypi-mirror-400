"""Tests for Tool class."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from pydantic import Field

from airops import Tool, ToolOutputs
from airops.inputs import Number, ShortText, ToolInputs


class SampleInputs(ToolInputs):
    url: ShortText = Field(..., description="URL to process")
    limit: Number = Field(default=10, description="Result limit")


class SampleOutputs(ToolOutputs):
    results: list[str]


def test_tool_initialization() -> None:
    """Tool can be initialized with models."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        input_model=SampleInputs,
        output_model=SampleOutputs,
    )

    assert tool.name == "test_tool"
    assert tool.description == "A test tool"
    assert tool.input_model == SampleInputs
    assert tool.output_model == SampleOutputs


def test_tool_schemas() -> None:
    """Tool exposes JSON schemas from models."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        input_model=SampleInputs,
        output_model=SampleOutputs,
    )

    inputs_schema = tool.inputs_schema
    assert "properties" in inputs_schema
    assert "url" in inputs_schema["properties"]
    assert "limit" in inputs_schema["properties"]

    outputs_schema = tool.outputs_schema
    assert "properties" in outputs_schema
    assert "results" in outputs_schema["properties"]


def test_handler_decorator() -> None:
    """Handler decorator registers function."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        input_model=SampleInputs,
        output_model=SampleOutputs,
    )

    @tool.handler
    async def run(inputs: SampleInputs) -> SampleOutputs:
        return SampleOutputs(results=[inputs.url])

    assert tool._handler is not None
    assert tool._handler == run


def test_app_requires_handler() -> None:
    """Accessing app without handler raises error."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        input_model=SampleInputs,
        output_model=SampleOutputs,
    )

    with pytest.raises(RuntimeError, match="No handler registered"):
        _ = tool.app


def test_app_creation() -> None:
    """App is created when handler is registered."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        input_model=SampleInputs,
        output_model=SampleOutputs,
    )

    @tool.handler
    async def run(inputs: SampleInputs) -> SampleOutputs:
        return SampleOutputs(results=[inputs.url])

    app = tool.app
    assert app is not None
    assert app.title == "test_tool"


def test_serve_loads_dotenv() -> None:
    """serve() loads environment variables from .env file."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        input_model=SampleInputs,
        output_model=SampleOutputs,
    )

    @tool.handler
    async def run(inputs: SampleInputs) -> SampleOutputs:
        return SampleOutputs(results=[inputs.url])

    with (
        patch("airops.tool.load_dotenv") as mock_load_dotenv,
        patch("airops.tool.uvicorn.run"),
    ):
        tool.serve(reload=False)
        mock_load_dotenv.assert_called_once()


@pytest.mark.parametrize("env_value", ["1", "true", "TRUE", "True"])
def test_serve_hot_reload_env_enabled(env_value: str) -> None:
    """serve() enables reload when HOT_RELOAD env var is set."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        input_model=SampleInputs,
        output_model=SampleOutputs,
    )

    @tool.handler
    async def run(inputs: SampleInputs) -> SampleOutputs:
        return SampleOutputs(results=[inputs.url])

    with (
        patch.dict("os.environ", {"HOT_RELOAD": env_value}),
        patch("airops.tool.load_dotenv"),
        patch("airops.tool.uvicorn.run") as mock_uvicorn,
    ):
        tool.serve()
        mock_uvicorn.assert_called_once()
        assert mock_uvicorn.call_args.kwargs["reload"] is True


@pytest.mark.parametrize("env_value", ["", "0", "false", "no"])
def test_serve_hot_reload_env_disabled(env_value: str) -> None:
    """serve() disables reload when HOT_RELOAD env var is not set or falsy."""
    tool = Tool(
        name="test_tool",
        description="A test tool",
        input_model=SampleInputs,
        output_model=SampleOutputs,
    )

    @tool.handler
    async def run(inputs: SampleInputs) -> SampleOutputs:
        return SampleOutputs(results=[inputs.url])

    with (
        patch.dict("os.environ", {"HOT_RELOAD": env_value}),
        patch("airops.tool.load_dotenv"),
        patch("airops.tool.uvicorn.run") as mock_uvicorn,
    ):
        tool.serve()
        mock_uvicorn.assert_called_once()
        # When reload is False, uvicorn.run is called with the app directly
        assert "reload" not in mock_uvicorn.call_args.kwargs
