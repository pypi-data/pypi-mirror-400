"""Common response DTOs."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DeleteResponse(BaseModel):
    """Generic delete response."""

    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """Health check response."""

    status: str


class DriverPoolStats(BaseModel):
    """Driver pool statistics."""

    pool_stats: dict[str, Any]


class ErrorDetail(BaseModel):
    """Error detail for Neo4j errors."""

    message: str
    error_code: str | None = None
    error_type: str | None = None


class ErrorResponse(BaseModel):
    """Error response with optional query."""

    error: ErrorDetail | None = None
    detail: str | None = None  # For HTTP exceptions
    query: str | None = None
    message: str | None = None
    error_type: str | None = None
