"""Client node model."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from .._base import BaseNode


class ClientNode(BaseNode):
    """Root node representing a client/organization."""

    label: Literal["Client"] = "Client"
    description: str | None = Field(None)
