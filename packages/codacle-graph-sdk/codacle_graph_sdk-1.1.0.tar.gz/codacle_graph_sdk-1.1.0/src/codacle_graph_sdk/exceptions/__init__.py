"""SDK exceptions."""

from __future__ import annotations

from typing import Any

from ._base import CodacleGraphError
from .auth import AuthenticationError, ForbiddenError
from .network import NetworkError
from .query import (
    LLMServiceError,
    Neo4jQueryError,
    ServerError,
    TranslationError,
)
from .resource import (
    ConflictError,
    InputValidationError,
    NotFoundError,
    ValidationError,
)

__all__ = [
    "CodacleGraphError",
    "AuthenticationError",
    "ForbiddenError",
    "NetworkError",
    "NotFoundError",
    "ValidationError",
    "InputValidationError",
    "ConflictError",
    "Neo4jQueryError",
    "TranslationError",
    "LLMServiceError",
    "ServerError",
    "raise_for_error",
]


def raise_for_error(status_code: int, data: dict[str, Any]) -> None:
    """Raise appropriate exception based on response."""
    detail = data.get("detail", "")
    message = data.get("message", detail)
    error = data.get("error", {})

    if status_code == 401:
        raise AuthenticationError(message or "Invalid API key", status_code)
    elif status_code == 403:
        raise ForbiddenError(message or "Access denied", status_code)
    elif status_code == 404:
        raise NotFoundError(message or "Resource not found", status_code)
    elif status_code == 409:
        raise ConflictError(message or "Resource conflict", status_code)
    elif status_code == 503:
        msg = message or "LLM service unavailable"
        raise LLMServiceError(msg, status_code)
    elif status_code >= 500:
        raise ServerError(message or "Server error", status_code)
    elif status_code == 400:
        error_type = data.get("error_type") or error.get("error_type", "")
        query = data.get("query") or error.get("query")

        if error_type in (
            "CYPHER_SYNTAX_ERROR",
            "CYPHER_SEMANTIC_ERROR",
            "DATABASE_ERROR",
        ):
            raise Neo4jQueryError(
                error.get("message", message),
                query=query,
                error_code=error.get("error_code"),
                error_type=error_type,
            )
        elif error_type in ("TRANSLATION_ERROR", "VALIDATION_ERROR"):
            raise TranslationError(message, query=query, error_type=error_type)
        else:
            raise ValidationError(message, status_code)
