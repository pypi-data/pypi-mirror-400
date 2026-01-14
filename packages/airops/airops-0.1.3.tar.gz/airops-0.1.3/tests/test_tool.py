"""Tests for Tool class."""

from __future__ import annotations

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
