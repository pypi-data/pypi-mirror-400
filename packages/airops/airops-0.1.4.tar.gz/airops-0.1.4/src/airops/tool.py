"""Tool class for defining AirOps tools."""

import inspect
import os
import types
from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any, TypeVar

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from airops.inputs import ToolInputs
from airops.inputs.schema import generate_airops_input_schema
from airops.outputs import ToolOutputs
from airops.server.app import create_app

InputT = TypeVar("InputT", bound=ToolInputs)
OutputT = TypeVar("OutputT", bound=ToolOutputs)
AsyncHandler = Callable[[InputT], Coroutine[Any, Any, OutputT]]


class Tool:
    """AirOps Tool definition.

    A Tool wraps an async handler function with input/output validation and
    provides a runtime server for local development and deployment.

    Example:
        from pydantic import Field
        from airops import Tool, steps
        from airops.inputs import ToolInputs, ShortText
        from airops.outputs import ToolOutputs

        class Inputs(ToolInputs):
            url: ShortText = Field(..., description="URL to search")

        class Outputs(ToolOutputs):
            results: list[dict]

        tool = Tool(
            name="my_tool",
            description="Search for a URL",
            input_model=Inputs,
            output_model=Outputs,
        )

        @tool.handler
        async def run(inputs: Inputs) -> Outputs:
            serp = await steps.execute("google_search", {"query": f"site:{inputs.url}"})
            return Outputs(results=serp["results"])

        if __name__ == "__main__":
            tool.serve()
    """

    def __init__(
        self,
        name: str,
        description: str,
        input_model: type[ToolInputs],
        output_model: type[ToolOutputs],
    ) -> None:
        """Initialize a tool.

        Args:
            name: Tool name (used in UI and API).
            description: Human-readable description of what the tool does.
            input_model: ToolInputs subclass defining the tool inputs.
            output_model: ToolOutputs subclass defining the tool outputs.
        """
        self.name = name
        self.description = description
        self.input_model = input_model
        self.output_model = output_model
        self._handler: AsyncHandler[Any, Any] | None = None
        self._app: FastAPI | None = None

    @property
    def inputs_schema(self) -> dict[str, Any]:
        """JSON schema for tool inputs."""
        return self.input_model.model_json_schema()

    @property
    def outputs_schema(self) -> dict[str, Any]:
        """JSON schema for tool outputs."""
        return self.output_model.model_json_schema()

    @property
    def airops_inputs_schema(self) -> list[dict[str, Any]]:
        """AirOps workflow input schema."""
        return generate_airops_input_schema(self.input_model)

    def handler(self, func: AsyncHandler[InputT, OutputT]) -> AsyncHandler[InputT, OutputT]:
        """Decorator to register the async tool handler function.

        Args:
            func: Async handler function that takes the input model and returns the output model.

        Returns:
            The original function (for chaining).

        Example:
            @tool.handler
            async def run(inputs: Inputs) -> Outputs:
                ...
        """
        self._handler = func
        return func

    @property
    def app(self) -> FastAPI:
        """Get the FastAPI ASGI application.

        Creates the app on first access using the registered handler.

        Raises:
            RuntimeError: If no handler has been registered.
        """
        if self._app is None:
            if self._handler is None:
                raise RuntimeError(
                    f"No handler registered for tool '{self.name}'. "
                    "Use @tool.handler decorator to register a handler."
                )
            self._app = create_app(
                tool_name=self.name,
                tool_description=self.description,
                handler=self._handler,
                input_model=self.input_model,
                output_model=self.output_model,
                ui=True,
            )
        return self._app

    @staticmethod
    def _get_caller_context(depth: int = 2) -> tuple[types.FrameType, types.ModuleType | None]:
        """Get the frame and module of the caller.

        Args:
            depth: How many frames to go back (default 2: caller of caller).
        """
        frame = inspect.currentframe()
        for _ in range(depth):
            assert frame is not None
            frame = frame.f_back
        assert frame is not None
        return frame, inspect.getmodule(frame)

    def _find_tool_var_name(
        self, caller_frame: types.FrameType, caller_module: types.ModuleType | None
    ) -> str:
        """Find the variable name holding this Tool instance in caller's scope."""
        for name, obj in caller_frame.f_locals.items():
            if obj is self:
                return name

        if caller_module is not None:
            for name, obj in vars(caller_module).items():
                if obj is self:
                    return name

        raise RuntimeError(
            "Could not detect tool variable name for hot reload. "
            "Ensure tool is assigned to a module-level variable."
        )

    def _print_startup_banner(
        self, host: str, port: int, ui: bool, watch_dir: str | None = None
    ) -> None:
        """Print server startup information."""
        reload_msg = " (hot reload enabled)" if watch_dir else ""
        print(f"Starting {self.name}{reload_msg}...")
        print(f"  API: http://{host}:{port}/runs")
        if ui:
            print(f"  UI:  http://{host}:{port}/")
        if watch_dir:
            print(f"  Watching: {watch_dir}")
        print()

    def serve(
        self,
        host: str = "0.0.0.0",
        port: int = 8080,
        *,
        ui: bool = True,
        reload: bool | None = None,
    ) -> None:
        """Run the tool as a local development server.

        Args:
            host: Host to bind to (default: "0.0.0.0").
            port: Port to listen on (default: 8080).
            ui: Enable local testing UI (default: True).
            reload: Enable hot reload on file changes. None (default) reads from
                    the HOT_RELOAD environment variable ("1" or "true" to enable).
        """
        load_dotenv()

        if self._handler is None:
            raise RuntimeError(
                f"No handler registered for tool '{self.name}'. "
                "Use @tool.handler decorator to register a handler."
            )

        caller_frame, caller_module = self._get_caller_context()

        if reload is None:
            hot_reload_env = os.environ.get("HOT_RELOAD", "").lower()
            reload = hot_reload_env in ("1", "true")

        if reload:
            assert caller_module is not None
            tool_var_name = self._find_tool_var_name(caller_frame, caller_module)
            module_file = Path(inspect.getfile(caller_module))
            watch_dir = str(module_file.parent)
            app_import = f"{module_file.stem}:{tool_var_name}.app"

            self._print_startup_banner(host, port, ui, watch_dir)
            uvicorn.run(
                app_import,
                host=host,
                port=port,
                reload=True,
                reload_dirs=[watch_dir],
            )
        else:
            self._app = create_app(
                tool_name=self.name,
                tool_description=self.description,
                handler=self._handler,
                input_model=self.input_model,
                output_model=self.output_model,
                ui=ui,
            )

            self._print_startup_banner(host, port, ui)
            uvicorn.run(self._app, host=host, port=port)
