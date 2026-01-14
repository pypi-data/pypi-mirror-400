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


_FALLBACK_MESSAGES: dict[int, str] = {
    400: "Bad request",
    401: "Invalid API key",
    403: "Access denied",
    404: "Resource not found",
    409: "Resource conflict",
    500: "Server error",
    503: "Service unavailable",
}


def raise_for_error(status_code: int, data: dict[str, Any]) -> None:
    """Raise appropriate exception based on response."""
    detail = data.get("detail", "")
    message = data.get("message") or detail
    error = data.get("error", {})

    # Try nested error.message if top-level message is empty
    if not message and isinstance(error, dict):
        message = error.get("message", "")

    # Fallback to status-code-specific default
    if not message:
        message = _FALLBACK_MESSAGES.get(status_code, "Request failed")

    if status_code == 401:
        raise AuthenticationError(message, status_code, response_data=data)
    elif status_code == 403:
        raise ForbiddenError(message, status_code, response_data=data)
    elif status_code == 404:
        raise NotFoundError(message, status_code, response_data=data)
    elif status_code == 409:
        raise ConflictError(message, status_code, response_data=data)
    elif status_code == 503:
        raise LLMServiceError(message, status_code, response_data=data)
    elif status_code >= 500:
        raise ServerError(message, status_code, response_data=data)
    elif status_code == 400:
        error_type = data.get("error_type") or error.get("error_type", "")
        query = data.get("query") or error.get("query")

        if error_type in (
            "CYPHER_SYNTAX_ERROR",
            "CYPHER_SEMANTIC_ERROR",
            "DATABASE_ERROR",
        ):
            raise Neo4jQueryError(
                error.get("message") or message,
                query=query,
                error_code=error.get("error_code"),
                error_type=error_type,
                response_data=data,
            )
        elif error_type in ("TRANSLATION_ERROR", "VALIDATION_ERROR"):
            raise TranslationError(
                message, query=query, error_type=error_type, response_data=data
            )
        else:
            raise ValidationError(message, status_code, response_data=data)
