"""Authentication and authorization exceptions."""

from __future__ import annotations

from ._base import CodacleGraphError


class AuthenticationError(CodacleGraphError):
    """Invalid or missing API key (401)."""

    pass


class ForbiddenError(CodacleGraphError):
    """Access denied to resource or alias (403)."""

    pass
