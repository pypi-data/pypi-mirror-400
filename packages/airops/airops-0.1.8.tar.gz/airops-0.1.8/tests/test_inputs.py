"""Tests for AirOps input types."""

from __future__ import annotations

from typing import get_args

import pytest
from pydantic import Field

from airops import Tool, ToolOutputs
from airops.inputs import (
    AirOpsInputMeta,
    Brandkit,
    Database,
    Json,
    KnowledgeBase,
    LongText,
    MultiSelect,
    Number,
    SelectInputMeta,
    ShortText,
    SingleSelect,
    ToolInputs,
    generate_airops_input_schema,
)


class TestMetadata:
    """Test metadata classes."""

    def test_airops_input_meta_frozen(self) -> None:
        """AirOpsInputMeta is immutable."""
        meta = AirOpsInputMeta(interface="short_text")
        with pytest.raises(AttributeError):
            meta.interface = "long_text"  # type: ignore[misc]

    def test_select_input_meta_requires_select_interface(self) -> None:
        """SelectInputMeta requires single_select or multi_select interface."""
        with pytest.raises(ValueError, match="single_select.*multi_select"):
            SelectInputMeta(interface="short_text", options=("a", "b"))  # type: ignore[arg-type]


class TestToolInputsValidation:
    """Test ToolInputs field validation."""

    def test_rejects_plain_str(self) -> None:
        """ToolInputs rejects plain str fields."""
        with pytest.raises(TypeError, match="invalid types.*'name'"):

            class Inputs(ToolInputs):
                name: str

    def test_rejects_plain_int(self) -> None:
        """ToolInputs rejects plain int fields."""
        with pytest.raises(TypeError, match="invalid types.*'count'"):

            class Inputs(ToolInputs):
                count: int

    def test_rejects_mixed_valid_invalid(self) -> None:
        """ToolInputs rejects class with any invalid field."""
        with pytest.raises(TypeError, match="invalid types.*'bad_field'"):

            class Inputs(ToolInputs):
                good_field: ShortText
                bad_field: str

    def test_accepts_all_valid_types(self) -> None:
        """ToolInputs accepts all valid AirOps input types."""

        class Inputs(ToolInputs):
            text: ShortText
            long: LongText
            num: Number
            data: Json
            single: SingleSelect("a", "b")
            multi: MultiSelect("x", "y")
            kb: KnowledgeBase
            brand: Brandkit
            db: Database

        # Should not raise
        assert Inputs is not None


class TestTypeAnnotations:
    """Test type annotation definitions."""

    def test_short_text_has_metadata(self) -> None:
        """ShortText carries short_text interface metadata."""
        args = get_args(ShortText)
        meta = next((a for a in args if isinstance(a, AirOpsInputMeta)), None)
        assert meta is not None
        assert meta.interface == "short_text"

    def test_long_text_has_metadata(self) -> None:
        """LongText carries long_text interface metadata."""
        args = get_args(LongText)
        meta = next((a for a in args if isinstance(a, AirOpsInputMeta)), None)
        assert meta is not None
        assert meta.interface == "long_text"

    def test_number_has_metadata(self) -> None:
        """Number carries number interface metadata."""
        args = get_args(Number)
        meta = next((a for a in args if isinstance(a, AirOpsInputMeta)), None)
        assert meta is not None
        assert meta.interface == "number"

    def test_json_has_metadata(self) -> None:
        """Json carries json interface metadata."""
        args = get_args(Json)
        meta = next((a for a in args if isinstance(a, AirOpsInputMeta)), None)
        assert meta is not None
        assert meta.interface == "json"

    def test_knowledge_base_has_metadata(self) -> None:
        """KnowledgeBase carries knowledge_base interface metadata."""
        args = get_args(KnowledgeBase)
        meta = next((a for a in args if isinstance(a, AirOpsInputMeta)), None)
        assert meta is not None
        assert meta.interface == "knowledge_base"

    def test_brandkit_has_metadata(self) -> None:
        """Brandkit carries brandkit interface metadata."""
        args = get_args(Brandkit)
        meta = next((a for a in args if isinstance(a, AirOpsInputMeta)), None)
        assert meta is not None
        assert meta.interface == "brandkit"

    def test_database_has_metadata(self) -> None:
        """Database carries database interface metadata."""
        args = get_args(Database)
        meta = next((a for a in args if isinstance(a, AirOpsInputMeta)), None)
        assert meta is not None
        assert meta.interface == "database"


class TestSelectTypes:
    """Test SingleSelect and MultiSelect factory functions."""

    def test_single_select_creates_annotated_type(self) -> None:
        """SingleSelect creates type with SelectInputMeta."""
        select_type = SingleSelect("json", "csv", "xml")
        args = get_args(select_type)
        meta = next((a for a in args if isinstance(a, SelectInputMeta)), None)
        assert meta is not None
        assert meta.interface == "single_select"
        assert meta.options == ("json", "csv", "xml")

    def test_single_select_accepts_metadata(self) -> None:
        """SingleSelect accepts label, placeholder, test_value."""
        select_type = SingleSelect(
            "a",
            "b",
            label="Format",
            placeholder="Choose one",
            test_value="a",
        )
        args = get_args(select_type)
        meta = next((a for a in args if isinstance(a, SelectInputMeta)), None)
        assert meta is not None
        assert meta.label == "Format"
        assert meta.placeholder == "Choose one"
        assert meta.test_value == "a"

    def test_multi_select_creates_annotated_type(self) -> None:
        """MultiSelect creates type with SelectInputMeta."""
        select_type = MultiSelect("urgent", "important", "low")
        args = get_args(select_type)
        meta = next((a for a in args if isinstance(a, SelectInputMeta)), None)
        assert meta is not None
        assert meta.interface == "multi_select"
        assert meta.options == ("urgent", "important", "low")


class TestSchemaGeneration:
    """Test generate_airops_input_schema function."""

    def test_basic_schema(self) -> None:
        """Generates schema with correct structure."""

        class Inputs(ToolInputs):
            query: ShortText = Field(..., description="Search query")
            limit: Number = Field(default=10)

        schema = generate_airops_input_schema(Inputs)

        assert len(schema) == 2

        query_field = next(f for f in schema if f["name"] == "query")
        assert query_field["interface"] == "short_text"
        assert query_field["required"] is True
        assert query_field["hint"] == "Search query"
        assert query_field["label"] == "Query"
        assert query_field["group_id"] == "no-group"

        limit_field = next(f for f in schema if f["name"] == "limit")
        assert limit_field["interface"] == "number"
        assert limit_field["required"] is False

    def test_select_includes_options(self) -> None:
        """Select types include options in schema."""

        class Inputs(ToolInputs):
            fmt: SingleSelect("json", "csv") = Field(default="json")

        schema = generate_airops_input_schema(Inputs)
        fmt_field = schema[0]
        assert fmt_field["interface"] == "single_select"
        assert fmt_field["options"] == ["json", "csv"]

    def test_resource_types(self) -> None:
        """Resource types have correct interfaces."""

        class Inputs(ToolInputs):
            kb: KnowledgeBase
            brand: Brandkit
            db: Database

        schema = generate_airops_input_schema(Inputs)

        kb_field = next(f for f in schema if f["name"] == "kb")
        assert kb_field["interface"] == "knowledge_base"

        brand_field = next(f for f in schema if f["name"] == "brand")
        assert brand_field["interface"] == "brandkit"

        db_field = next(f for f in schema if f["name"] == "db")
        assert db_field["interface"] == "database"

    def test_humanizes_field_name_for_label(self) -> None:
        """Field names are converted to title case for labels."""

        class Inputs(ToolInputs):
            search_query: ShortText
            max_results: Number

        schema = generate_airops_input_schema(Inputs)

        query_field = next(f for f in schema if f["name"] == "search_query")
        assert query_field["label"] == "Search Query"

        results_field = next(f for f in schema if f["name"] == "max_results")
        assert results_field["label"] == "Max Results"


class TestToolIntegration:
    """Test integration with Tool class."""

    def test_tool_airops_inputs_schema(self) -> None:
        """Tool.airops_inputs_schema returns AirOps format."""

        class Inputs(ToolInputs):
            query: ShortText = Field(..., description="Search query")
            limit: Number = Field(default=10)

        class Outputs(ToolOutputs):
            results: list[str]

        tool = Tool(
            name="test",
            description="Test tool",
            input_model=Inputs,
            output_model=Outputs,
        )

        schema = tool.airops_inputs_schema
        assert isinstance(schema, list)
        assert len(schema) == 2
        assert schema[0]["name"] == "query"
        assert schema[0]["interface"] == "short_text"
        assert schema[1]["name"] == "limit"
        assert schema[1]["interface"] == "number"


class TestJsonSchemaCompatibility:
    """Test JSON schema compatibility with FastUI form rendering."""

    def test_no_unsupported_anyof_in_schema(self) -> None:
        """Input types must not generate anyOf schemas (FastUI limitation).

        FastUI's form renderer only supports anyOf for optional types (X | None).
        Union types like int | float generate anyOf with multiple non-null types,
        which FastUI cannot render.
        """

        class Inputs(ToolInputs):
            text: ShortText
            long: LongText
            num: Number
            data: Json
            single: SingleSelect("a", "b")
            multi: MultiSelect("x", "y")
            kb: KnowledgeBase
            brand: Brandkit
            db: Database

        schema = Inputs.model_json_schema()
        properties = schema.get("properties", {})

        for field_name, field_schema in properties.items():
            if "anyOf" in field_schema:
                any_of = field_schema["anyOf"]
                non_null_types = [t for t in any_of if t != {"type": "null"}]
                assert len(non_null_types) <= 1, (
                    f"Field '{field_name}' has anyOf with multiple non-null types: "
                    f"{non_null_types}. FastUI only supports anyOf for optional types."
                )


class TestPydanticValidation:
    """Test that types work with Pydantic validation."""

    def test_short_text_validates(self) -> None:
        """ShortText validates as string."""

        class Inputs(ToolInputs):
            query: ShortText

        inputs = Inputs(query="test")
        assert inputs.query == "test"

    def test_number_validates(self) -> None:
        """Number validates as int or float."""

        class Inputs(ToolInputs):
            count: Number

        inputs_int = Inputs(count=10)
        assert inputs_int.count == 10

        inputs_float = Inputs(count=10.5)
        assert inputs_float.count == 10.5

    def test_resource_types_validate_as_int(self) -> None:
        """Resource types validate as int."""

        class Inputs(ToolInputs):
            kb: KnowledgeBase
            brand: Brandkit
            db: Database

        inputs = Inputs(kb=1, brand=2, db=3)
        assert inputs.kb == 1
        assert inputs.brand == 2
        assert inputs.db == 3

    def test_single_select_validates(self) -> None:
        """SingleSelect validates as string."""

        class Inputs(ToolInputs):
            fmt: SingleSelect("json", "csv")

        inputs = Inputs(fmt="json")
        assert inputs.fmt == "json"

    def test_multi_select_validates(self) -> None:
        """MultiSelect validates as list of strings."""

        class Inputs(ToolInputs):
            tags: MultiSelect("a", "b", "c")

        inputs = Inputs(tags=["a", "b"])
        assert inputs.tags == ["a", "b"]
