"""Object node model."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from .._base import BaseNode


class ObjectNode(BaseNode):
    """Object instance."""

    label: Literal["Object"] = "Object"
    class_name: str | None = Field(
        None, description="Class this object instantiates"
    )
