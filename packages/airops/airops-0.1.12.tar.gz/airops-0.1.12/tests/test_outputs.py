"""Tests for ToolOutputs."""

from airops.outputs import ToolOutputs


class TestToolOutputs:
    """Test ToolOutputs base class."""

    def test_subclass_works(self) -> None:
        """ToolOutputs can be subclassed."""

        class Outputs(ToolOutputs):
            text: str
            count: int

        outputs = Outputs(text="hello", count=5)
        assert outputs.text == "hello"
        assert outputs.count == 5

    def test_model_dump(self) -> None:
        """ToolOutputs supports Pydantic model_dump."""

        class Outputs(ToolOutputs):
            results: list[str]

        outputs = Outputs(results=["a", "b"])
        assert outputs.model_dump() == {"results": ["a", "b"]}
