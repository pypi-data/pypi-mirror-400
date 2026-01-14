"""Application node model."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from .._base import BaseNode


class ApplicationNode(BaseNode):
    """Application belonging to a client."""

    label: Literal["Application"] = "Application"
    version: str | None = Field(None)
    language: str | None = Field(None)
