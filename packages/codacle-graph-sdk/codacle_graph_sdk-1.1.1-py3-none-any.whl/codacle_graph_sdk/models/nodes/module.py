"""Module node model."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from .._base import BaseNode


class ModuleNode(BaseNode):
    """Code module (file/package)."""

    label: Literal["Module"] = "Module"
    path: str | None = Field(None, description="File path")
    docstring: str | None = Field(None)
