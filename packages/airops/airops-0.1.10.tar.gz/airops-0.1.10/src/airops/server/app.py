"""FastAPI application factory for tool runtime."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

from airops.server.routes import create_routes
from airops.server.store import RunStore, get_store
from airops.server.ui import create_ui_routes


def create_app(
    tool_name: str,
    tool_description: str,
    handler: Callable[[Any], Any],
    input_model: type[BaseModel],
    output_model: type[BaseModel],
    *,
    ui: bool = True,
    store: RunStore | None = None,
) -> FastAPI:
    """Create a FastAPI application for a tool.

    Args:
        tool_name: Name of the tool.
        tool_description: Description of the tool.
        handler: The tool handler function.
        input_model: Pydantic model for input validation.
        output_model: Pydantic model for output validation.
        ui: Whether to enable the local testing UI (default: True).
        store: Optional run store (uses global store if not provided).

    Returns:
        Configured FastAPI application.
    """
    app = FastAPI(
        title=tool_name,
        description=tool_description,
        version="1.0.0",
    )

    # Use provided store or global store
    run_store = store or get_store()

    # Add API routes
    api_routes = create_routes(run_store, handler, input_model, output_model)
    app.include_router(api_routes)

    # Add UI routes if enabled
    if ui:
        ui_routes = create_ui_routes(
            tool_name, tool_description, input_model, output_model, handler, run_store
        )
        app.include_router(ui_routes)

    return app
