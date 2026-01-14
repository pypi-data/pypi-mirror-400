"""AirOps Python SDK for building custom tools.

Example:
    from pydantic import Field
    from airops import Tool, steps
    from airops.inputs import ToolInputs, ShortText
    from airops.outputs import ToolOutputs

    class Inputs(ToolInputs):
        url: ShortText = Field(..., description="URL to analyze")

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

from importlib.metadata import version as _get_version

from airops import inputs, secrets, steps
from airops.outputs import ToolOutputs
from airops.tool import Tool

__version__ = _get_version("airops")

__all__ = [
    "__version__",
    "Tool",
    "ToolOutputs",
    "steps",
    "secrets",
    "inputs",
]
