"""AirOps input types for tool definitions.

This module provides type annotations that define how tool inputs
appear in the AirOps UI and workflow builder.

Example:
    from pydantic import Field
    from airops.inputs import ToolInputs, ShortText, Number, SingleSelect

    class Inputs(ToolInputs):
        query: ShortText = Field(..., description="Search query")
        limit: Number = Field(default=10)
        format: SingleSelect("json", "csv", "xml") = Field(default="json")
"""

from __future__ import annotations

from typing import Any, get_args, get_type_hints

from pydantic import BaseModel

from airops.inputs.metadata import AirOpsInputMeta, InterfaceType, SelectInputMeta
from airops.inputs.schema import generate_airops_input_schema
from airops.inputs.types import (
    Brandkit,
    Database,
    Json,
    JsonValue,
    KnowledgeBase,
    LongText,
    MultiSelect,
    Number,
    ShortText,
    SingleSelect,
)


def _has_airops_meta(annotation: Any) -> bool:
    """Check if an annotation has AirOpsInputMeta attached."""
    args = get_args(annotation)
    return any(isinstance(arg, AirOpsInputMeta) for arg in args)


def _validate_input_fields(cls: type) -> None:
    """Validate that all fields use valid AirOps input types."""
    try:
        hints = get_type_hints(cls, include_extras=True)
    except Exception:
        return

    invalid_fields: list[str] = []
    for field_name, annotation in hints.items():
        if field_name.startswith("_"):
            continue
        if not _has_airops_meta(annotation):
            invalid_fields.append(field_name)

    if invalid_fields:
        fields_str = ", ".join(f"'{f}'" for f in invalid_fields)
        raise TypeError(
            f"{cls.__name__} has fields with invalid types: {fields_str}. "
            f"All fields must use AirOps input types "
            f"(ShortText, LongText, Number, Json, SingleSelect, MultiSelect, "
            f"KnowledgeBase, Brandkit, Database)."
        )


class ToolInputs(BaseModel):
    """Base class for tool input definitions.

    All tool input models must inherit from this class and use
    AirOps input types for all fields.

    Example:
        class Inputs(ToolInputs):
            query: ShortText = Field(..., description="Search query")
            limit: Number = Field(default=10)

    Raises:
        TypeError: If any field does not use a valid AirOps input type.
    """

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        _validate_input_fields(cls)


__all__ = [
    "ToolInputs",
    "ShortText",
    "LongText",
    "Number",
    "Json",
    "JsonValue",
    "SingleSelect",
    "MultiSelect",
    "KnowledgeBase",
    "Brandkit",
    "Database",
    "AirOpsInputMeta",
    "SelectInputMeta",
    "InterfaceType",
    "generate_airops_input_schema",
]
