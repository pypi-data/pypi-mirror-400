"""Subroutine node model."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from .._base import BaseNode


class SubroutineNode(BaseNode):
    """Function or method."""

    label: Literal["Subroutine"] = "Subroutine"
    signature: str | None = Field(None)
    docstring: str | None = Field(None)
    is_async: bool = Field(False)
    return_type: str | None = Field(None)
