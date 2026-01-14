"""Attribute node model."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from .._base import BaseNode


class AttributeNode(BaseNode):
    """Class or module attribute."""

    label: Literal["Attribute"] = "Attribute"
    type_annotation: str | None = Field(None)
    default_value: str | None = Field(None)
