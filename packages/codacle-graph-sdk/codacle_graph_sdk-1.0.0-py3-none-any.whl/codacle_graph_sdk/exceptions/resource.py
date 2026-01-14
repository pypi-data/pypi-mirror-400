"""Resource-related exceptions."""

from __future__ import annotations

from ._base import CodacleGraphError


class NotFoundError(CodacleGraphError):
    """Resource not found (404)."""

    pass


class ValidationError(CodacleGraphError):
    """Request validation failed (400)."""

    pass


class ConflictError(CodacleGraphError):
    """Duplicate resource conflict (409)."""

    pass
