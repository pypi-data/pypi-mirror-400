"""Metadata classes for AirOps input type annotations."""

from __future__ import annotations

import dataclasses
from typing import Any, Literal

InterfaceType = Literal[
    "short_text",
    "long_text",
    "number",
    "json",
    "single_select",
    "multi_select",
    "knowledge_base",
    "brandkit",
    "database",
]


@dataclasses.dataclass(frozen=True, slots=True)
class AirOpsInputMeta:
    """Metadata for AirOps input types.

    Attached to Annotated types and used during schema generation
    to produce the AirOps workflow input format.
    """

    interface: InterfaceType
    label: str | None = None
    placeholder: str | None = None
    test_value: Any = None


@dataclasses.dataclass(frozen=True, slots=True)
class SelectInputMeta(AirOpsInputMeta):
    """Metadata for single_select and multi_select inputs."""

    options: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.interface not in ("single_select", "multi_select"):
            raise ValueError(
                f"SelectInputMeta requires interface 'single_select' or "
                f"'multi_select', got '{self.interface}'"
            )
