"""HTTP routes for the tool runtime server."""

from __future__ import annotations

import traceback as tb
from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from airops.server.store import RunError, RunStore

router = APIRouter()


class StartRunRequest(BaseModel):
    """Request body for starting a run."""

    inputs: dict[str, Any]


class StartRunResponse(BaseModel):
    """Response for starting a run."""

    run_id: str
    status: str


class RunErrorResponse(BaseModel):
    """Error details in run response."""

    code: str
    message: str
    details: dict[str, Any] | None = None
    traceback: str | None = None


class GetRunResponse(BaseModel):
    """Response for getting run status."""

    run_id: str
    status: str
    outputs: dict[str, Any] | None = None
    error: RunErrorResponse | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str


HandlerFunc = Callable[[Any], Coroutine[Any, Any, Any]]


def create_routes(
    store: RunStore,
    handler: HandlerFunc,
    input_model: type[BaseModel],
    output_model: type[BaseModel],
) -> APIRouter:
    """Create API routes for a tool.

    Args:
        store: The run store for tracking executions.
        handler: The tool handler function.
        input_model: Pydantic model for input validation.
        output_model: Pydantic model for output validation.

    Returns:
        FastAPI router with configured routes.
    """
    routes = APIRouter()

    @routes.post("/runs", response_model=StartRunResponse, status_code=202)
    async def start_run(
        request: StartRunRequest,
        background_tasks: BackgroundTasks,
    ) -> StartRunResponse:
        """Start a new tool run."""
        # Validate inputs against the input model
        try:
            validated_inputs = input_model.model_validate(request.inputs)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        # Create the run
        run = store.create(request.inputs)

        # Execute in background
        background_tasks.add_task(
            execute_handler,
            store,
            run.run_id,
            handler,
            validated_inputs,
            output_model,
        )

        return StartRunResponse(
            run_id=run.run_id,
            status=run.status.value,
        )

    @routes.get("/runs/{run_id}", response_model=GetRunResponse)
    async def get_run(run_id: str) -> GetRunResponse:
        """Get the status of a run."""
        run = store.get(run_id)

        if run is None:
            raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

        error_response = None
        if run.error:
            error_response = RunErrorResponse(
                code=run.error.code,
                message=run.error.message,
                details=run.error.details,
                traceback=run.error.traceback,
            )

        return GetRunResponse(
            run_id=run.run_id,
            status=run.status.value,
            outputs=run.outputs,
            error=error_response,
        )

    @routes.get("/health", response_model=HealthResponse)
    async def health_check() -> HealthResponse:
        """Health check endpoint."""
        return HealthResponse(status="ok")

    return routes


async def execute_handler(
    store: RunStore,
    run_id: str,
    handler: HandlerFunc,
    inputs: BaseModel,
    output_model: type[BaseModel],
) -> None:
    """Execute the handler in background and update run state.

    Args:
        store: The run store.
        run_id: The run ID to update.
        handler: Async tool handler function.
        inputs: Validated input model instance.
        output_model: Pydantic model for output validation.
    """
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
