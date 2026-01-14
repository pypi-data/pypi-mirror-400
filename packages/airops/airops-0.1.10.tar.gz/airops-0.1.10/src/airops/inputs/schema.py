"""Schema generation for AirOps input types."""

from __future__ import annotations

from typing import Any, get_args, get_origin, get_type_hints

from pydantic import BaseModel

from airops.inputs.metadata import AirOpsInputMeta, SelectInputMeta

DEFAULT_INTERFACE_MAP: dict[type, str] = {
    str: "short_text",
    int: "number",
    float: "number",
    dict: "json",
    list: "json",
}


def _extract_airops_meta(annotation: Any) -> AirOpsInputMeta | None:
    """Extract AirOpsInputMeta from an Annotated type."""
    args = get_args(annotation)
    for arg in args:
        if isinstance(arg, AirOpsInputMeta):
            return arg
    return None


def _get_base_type(annotation: Any) -> type | None:
    """Get the base type from an Annotated type or return the type itself."""
    origin = get_origin(annotation)
    if origin is not None:
        args = get_args(annotation)
        if args:
            first_arg = args[0]
            if isinstance(first_arg, type):
                return first_arg
            return None
    if isinstance(annotation, type):
        return annotation
    return None


def _infer_interface(annotation: Any) -> str:
    """Infer the AirOps interface type from annotation."""
    meta = _extract_airops_meta(annotation)
    if meta is not None:
        return meta.interface

    base_type = _get_base_type(annotation)
    if base_type is not None and base_type in DEFAULT_INTERFACE_MAP:
        return DEFAULT_INTERFACE_MAP[base_type]

    return "short_text"


def _humanize_field_name(name: str) -> str:
    """Convert field_name to 'Field Name' for label."""
    return name.replace("_", " ").title()


def generate_airops_input_schema(model: type[BaseModel]) -> list[dict[str, Any]]:
    """Generate AirOps workflow input schema from a Pydantic model.

    Args:
        model: Pydantic BaseModel class with input field definitions.

    Returns:
        List of input schema objects matching AirOps workflow format.
    """
    inputs: list[dict[str, Any]] = []
    type_hints = get_type_hints(model, include_extras=True)

    for field_name, field_info in model.model_fields.items():
        annotation = type_hints.get(field_name, field_info.annotation)
        meta = _extract_airops_meta(annotation)

        entry: dict[str, Any] = {
            "name": field_name,
            "interface": _infer_interface(annotation),
            "required": field_info.is_required(),
            "group_id": "no-group",
        }

        if meta and meta.label:
            entry["label"] = meta.label
        else:
            entry["label"] = _humanize_field_name(field_name)

        if field_info.description:
            entry["hint"] = field_info.description

        if meta and meta.placeholder:
            entry["placeholder"] = meta.placeholder

        if meta and meta.test_value is not None:
            entry["test_value"] = meta.test_value

        if isinstance(meta, SelectInputMeta) and meta.options:
            entry["options"] = list(meta.options)

        inputs.append(entry)

    return inputs
