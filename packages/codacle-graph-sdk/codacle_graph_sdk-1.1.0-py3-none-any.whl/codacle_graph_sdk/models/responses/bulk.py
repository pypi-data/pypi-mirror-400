"""Bulk insert response DTOs."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class BulkInsertResult(BaseModel):
    """Single bulk insert operation result."""

    type: str  # "node" | "relationship"
    result: list[Any]


class BulkInsertResponse(BaseModel):
    """Bulk insert response."""

    message: str
    results: list[BulkInsertResult]
