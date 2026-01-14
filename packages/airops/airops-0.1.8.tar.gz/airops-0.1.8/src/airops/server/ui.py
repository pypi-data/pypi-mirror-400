"""Local testing UI for tools using FastUI.

Generates a form from the tool's Pydantic input model using FastUI.
"""

from __future__ import annotations

import traceback as tb
from collections.abc import Callable, Coroutine
from typing import Annotated, Any, Literal, get_args, get_origin

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import HTMLResponse
from fastui import AnyComponent, FastUI, prebuilt_html
from fastui import components as c
from fastui.components.forms import FormFieldTextarea
from fastui.events import GoToEvent
from fastui.forms import SelectOption
from pydantic import BaseModel

from airops.inputs.metadata import SelectInputMeta
from airops.server.store import RunError, RunStatus, RunStore

AsyncHandler = Callable[[Any], Coroutine[Any, Any, Any]]

HtmlInputType = Literal[
    "text", "date", "datetime-local", "time", "email", "url", "number", "password", "hidden"
]


def _get_select_meta(metadata: list[Any]) -> SelectInputMeta | None:
    """Extract SelectInputMeta from field metadata if present."""
    for item in metadata:
        if isinstance(item, SelectInputMeta):
            return item
    return None


def _humanize(name: str) -> str:
    """Convert snake_case to Title Case."""
    return name.replace("_", " ").title()


def _get_html_type(annotation: Any) -> HtmlInputType:
    """Determine HTML input type from annotation."""
    base_type = annotation
    if get_origin(annotation) is Annotated:
        args = get_args(annotation)
        base_type = args[0] if args else annotation

    if base_type in (int, float):
        return "number"

    if hasattr(base_type, "__name__") and base_type.__name__ in ("int", "float"):
        return "number"

    return "text"


FormFieldType = (
    c.FormFieldInput
    | FormFieldTextarea
    | c.FormFieldBoolean
    | c.FormFieldFile
    | c.FormFieldSelect
    | c.FormFieldSelectSearch
)


def _build_form_fields(model: type[BaseModel]) -> list[FormFieldType]:
    """Build form fields from a Pydantic model, handling select types."""
    fields: list[FormFieldType] = []

    for name, field_info in model.model_fields.items():
        annotation = field_info.annotation
        title = _humanize(name)
        required = field_info.is_required()
        description = field_info.description

        select_meta = _get_select_meta(field_info.metadata)

        if select_meta is not None:
            options = [SelectOption(value=opt, label=opt) for opt in select_meta.options]
            is_multi = select_meta.interface == "multi_select"

            initial: str | list[str] | None = None
            if field_info.default is not None and field_info.default is not ...:
                initial = field_info.default

            fields.append(
                c.FormFieldSelect(
                    name=name,
                    title=title,
                    required=required,
                    description=description,
                    options=options,
                    multiple=is_multi if is_multi else None,
                    initial=initial,
                    placeholder=select_meta.placeholder,
                )
            )
        else:
            initial_val: str | float | None = None
            if field_info.default is not None and field_info.default is not ...:
                default = field_info.default
                if isinstance(default, (str, int, float)):
                    initial_val = default

            html_type = _get_html_type(annotation)

            fields.append(
                c.FormFieldInput(
                    name=name,
                    title=title,
                    required=required,
                    description=description,
                    html_type=html_type,
                    initial=initial_val,
                )
            )

    return fields


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
        form_fields = _build_form_fields(input_model)
        return [
            c.Page(
                components=[
                    c.Heading(text=tool_name, level=1),
                    c.Paragraph(text=tool_description),
                    c.Form(
                        form_fields=form_fields,
                        submit_url="/api/submit",
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
                    c.Button(text="Refresh", on_click=GoToEvent(url=f"/run/{run_id}")),
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
            traceback_text = run.error.traceback if run.error else None
            components.extend(
                [
                    c.Paragraph(text="Status: error"),
                    c.Heading(text="Error", level=4),
                    c.Code(language="text", text=error_text),
                ]
            )
            if traceback_text:
                components.extend(
                    [
                        c.Heading(text="Stack Trace", level=4),
                        c.Code(language="python", text=traceback_text),
                    ]
                )
            components.extend(
                [
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
                traceback=tb.format_exc(),
            ),
        )


def _format_json(data: Any) -> str:
    """Format data as pretty JSON string."""
    import json

    if data is None:
        return "{}"
    return json.dumps(data, indent=2, default=str)
