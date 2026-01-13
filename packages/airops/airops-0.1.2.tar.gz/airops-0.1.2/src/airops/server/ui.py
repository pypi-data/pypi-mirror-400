"""Local testing UI for tools using FastUI.

Generates a form from the tool's Pydantic input model using FastUI's ModelForm.
"""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import HTMLResponse
from fastui import AnyComponent, FastUI, prebuilt_html
from fastui import components as c
from fastui.events import GoToEvent, PageEvent
from pydantic import BaseModel

from airops.server.store import RunError, RunStatus, RunStore

AsyncHandler = Callable[[Any], Coroutine[Any, Any, Any]]


def create_ui_routes(
    tool_name: str,
    tool_description: str,
    input_model: type[BaseModel],
    output_model: type[BaseModel],
    handler: AsyncHandler,
    store: RunStore,
) -> APIRouter:
    """Create UI routes for a tool using FastUI.

    Args:
        tool_name: Name of the tool.
        tool_description: Description of the tool.
        input_model: Pydantic model for inputs.
        output_model: Pydantic model for outputs.
        handler: Async tool handler function.
        store: The run store for tracking executions.

    Returns:
        FastAPI router with UI routes.
    """
    ui_router = APIRouter()

    @ui_router.get("/api/", response_model=FastUI, response_model_exclude_none=True)
    def ui_home() -> list[AnyComponent]:
        """Main UI page with form."""
        return [
            c.Page(
                components=[
                    c.Heading(text=tool_name, level=1),
                    c.Paragraph(text=tool_description),
                    c.ModelForm(
                        model=input_model,
                        submit_url="/api/submit",
                        display_mode="default",
                    ),
                ]
            ),
        ]

    @ui_router.post("/api/submit", response_model=FastUI, response_model_exclude_none=True)
    async def ui_submit(
        request: Request,
        background_tasks: BackgroundTasks,
    ) -> list[AnyComponent]:
        """Handle form submission and start a run."""
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            form_dict = await request.json()
        else:
            form_data = await request.form()
            form_dict = dict(form_data)

        validated = input_model.model_validate(form_dict)
        run = store.create(validated.model_dump())

        background_tasks.add_task(
            _execute_handler,
            store,
            run.run_id,
            handler,
            validated,
            output_model,
        )

        return [
            c.FireEvent(event=GoToEvent(url=f"/run/{run.run_id}")),
        ]

    @ui_router.get("/api/run/{run_id}", response_model=FastUI, response_model_exclude_none=True)
    async def ui_run_status(run_id: str) -> list[AnyComponent]:
        """Show run status and results."""
        run = store.get(run_id)

        if run is None:
            return [
                c.Page(
                    components=[
                        c.Heading(text="Run Not Found", level=1),
                        c.Paragraph(text=f"Run {run_id} not found."),
                        c.Link(
                            components=[c.Text(text="Back to form")],
                            on_click=GoToEvent(url="/"),
                        ),
                    ]
                ),
            ]

        components: list[AnyComponent] = [
            c.Heading(text=tool_name, level=1),
            c.Heading(text=f"Run: {run_id[:8]}...", level=3),
        ]

        if run.status in (RunStatus.QUEUED, RunStatus.RUNNING):
            components.extend(
                [
                    c.Paragraph(text=f"Status: {run.status.value}"),
                    c.Spinner(text="Running..."),
                    c.Paragraph(text=""),
                    c.Button(text="Refresh", on_click=PageEvent(name="reload")),
                ]
            )
        elif run.status == RunStatus.SUCCESS:
            components.extend(
                [
                    c.Paragraph(text="Status: success"),
                    c.Heading(text="Outputs", level=4),
                    c.Code(language="json", text=_format_json(run.outputs)),
                    c.Paragraph(text=""),
                    c.Link(
                        components=[c.Text(text="Run again")],
                        on_click=GoToEvent(url="/"),
                    ),
                ]
            )
        elif run.status == RunStatus.ERROR:
            error_text = run.error.message if run.error else "Unknown error"
            components.extend(
                [
                    c.Paragraph(text="Status: error"),
                    c.Heading(text="Error", level=4),
                    c.Code(language="text", text=error_text),
                    c.Paragraph(text=""),
                    c.Link(
                        components=[c.Text(text="Try again")],
                        on_click=GoToEvent(url="/"),
                    ),
                ]
            )

        return [c.Page(components=components)]

    @ui_router.get("/{path:path}")
    async def ui_html(path: str) -> HTMLResponse:
        """Serve the FastUI prebuilt HTML."""
        return HTMLResponse(prebuilt_html(title=tool_name))

    return ui_router


async def _execute_handler(
    store: RunStore,
    run_id: str,
    handler: AsyncHandler,
    inputs: BaseModel,
    output_model: type[BaseModel],
) -> None:
    """Execute the async handler and update run state."""
    store.set_running(run_id)

    try:
        result = await handler(inputs)

        # Validate output
        if isinstance(result, output_model):
            outputs = result.model_dump()
        elif isinstance(result, dict):
            validated = output_model.model_validate(result)
            outputs = validated.model_dump()
        else:
            outputs = output_model.model_validate(result).model_dump()

        store.set_success(run_id, outputs)

    except Exception as e:
        store.set_error(
            run_id,
            RunError(
                code="EXECUTION_ERROR",
                message=str(e),
                details={"type": type(e).__name__},
            ),
        )


def _format_json(data: Any) -> str:
    """Format data as pretty JSON string."""
    import json

    if data is None:
        return "{}"
    return json.dumps(data, indent=2, default=str)
