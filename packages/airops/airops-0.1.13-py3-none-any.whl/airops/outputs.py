"""Tool outputs base class."""

from pydantic import BaseModel


class ToolOutputs(BaseModel):
    """Base class for tool output definitions.

    All tool output models must inherit from this class.

    Example:
        class Outputs(ToolOutputs):
            results: list[dict[str, str]]
            count: int
    """

    pass
