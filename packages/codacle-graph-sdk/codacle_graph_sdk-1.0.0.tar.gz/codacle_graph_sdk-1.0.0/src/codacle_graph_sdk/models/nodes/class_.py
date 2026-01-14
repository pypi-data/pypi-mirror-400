"""Class node model."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from .._base import BaseNode


class ClassNode(BaseNode):
    """Class definition."""

    label: Literal["Class"] = "Class"
    docstring: str | None = Field(None)
    is_abstract: bool = Field(False)
    bases: list[str] = Field(
        default_factory=list, description="Base class names"
    )
