"""AirOps input type annotations.

These types provide semantic meaning for tool inputs and enable
automatic generation of AirOps workflow input schemas.
"""

from __future__ import annotations

from typing import Annotated, Any

from airops.inputs.metadata import AirOpsInputMeta, SelectInputMeta

type JsonValue = dict[str, JsonValue] | list[JsonValue] | str | int | float | bool | None

ShortText = Annotated[str, AirOpsInputMeta(interface="short_text")]
"""Short text input for single-line strings."""

LongText = Annotated[str, AirOpsInputMeta(interface="long_text")]
"""Long text input for multi-line strings."""

Number = Annotated[float, AirOpsInputMeta(interface="number")]
"""Numeric input supporting integers and floats."""

Json = Annotated[JsonValue, AirOpsInputMeta(interface="json")]
"""JSON input accepting any valid JSON value."""

KnowledgeBase = Annotated[int, AirOpsInputMeta(interface="knowledge_base")]
"""Knowledge base resource ID."""

Brandkit = Annotated[int, AirOpsInputMeta(interface="brandkit")]
"""Brandkit resource ID."""

Database = Annotated[int, AirOpsInputMeta(interface="database")]
"""Database resource ID."""


def SingleSelect(  # noqa: N802
    *options: str,
    label: str | None = None,
    placeholder: str | None = None,
    test_value: str | None = None,
) -> Any:
    """Create a single-select input type with specified options.

    Args:
        *options: Valid option values for selection.
        label: Optional display label.
        placeholder: Optional placeholder text.
        test_value: Optional test value.

    Returns:
        Annotated type for single selection.

    Example:
        class Inputs(BaseModel):
            format: SingleSelect("json", "csv", "xml") = "json"
    """
    return Annotated[
        str,
        SelectInputMeta(
            interface="single_select",
            options=options,
            label=label,
            placeholder=placeholder,
            test_value=test_value,
        ),
    ]


def MultiSelect(  # noqa: N802
    *options: str,
    label: str | None = None,
    placeholder: str | None = None,
    test_value: list[str] | None = None,
) -> Any:
    """Create a multi-select input type with specified options.

    Args:
        *options: Valid option values for selection.
        label: Optional display label.
        placeholder: Optional placeholder text.
        test_value: Optional test value (list of selected options).

    Returns:
        Annotated type for multiple selection.

    Example:
        class Inputs(BaseModel):
            tags: MultiSelect("urgent", "important", "low") = []
    """
    return Annotated[
        list[str],
        SelectInputMeta(
            interface="multi_select",
            options=options,
            label=label,
            placeholder=placeholder,
            test_value=test_value,
        ),
    ]
