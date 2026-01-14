"""Query execution exceptions."""

from __future__ import annotations

from ._base import CodacleGraphError


class Neo4jQueryError(CodacleGraphError):
    """Neo4j query execution error."""

    def __init__(
        self,
        message: str,
        query: str | None = None,
        error_code: str | None = None,
        error_type: str | None = None,
    ):
        super().__init__(message, status_code=400)
        self.query = query
        self.error_code = error_code
        self.error_type = error_type


class TranslationError(CodacleGraphError):
    """NL to Cypher translation failed."""

    def __init__(
        self,
        message: str,
        query: str | None = None,
        error_type: str | None = None,
    ):
        super().__init__(message, status_code=400)
        self.query = query
        self.error_type = error_type


class LLMServiceError(CodacleGraphError):
    """LLM service unavailable (503)."""

    pass


class ServerError(CodacleGraphError):
    """Internal server error (500)."""

    pass
