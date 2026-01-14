"""Resource-related exceptions."""

from __future__ import annotations

from typing import Any

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


class InputValidationError(ValidationError):
    """Raised when client-side input validation fails.

    This is raised BEFORE sending a request to the server,
    unlike ValidationError which is raised for server-side validation.
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any = None,
    ) -> None:
        super().__init__(message, status_code=None)
        self.field = field
        self.value = value
