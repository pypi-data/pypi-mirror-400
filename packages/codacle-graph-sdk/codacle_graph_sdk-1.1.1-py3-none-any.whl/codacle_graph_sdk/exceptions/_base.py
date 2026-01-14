"""Base exception for SDK errors."""

from __future__ import annotations

from typing import Any


class CodacleGraphError(Exception):
    """Base exception for all Codacle Graph SDK errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
        response_data: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.response_data = response_data or {}
        super().__init__(message)

    def __str__(self) -> str:
        if self.status_code and self.message:
            return f"[{self.status_code}] {self.message}"
        if self.status_code:
            return f"[{self.status_code}] {self.__class__.__name__}"
        if self.message:
            return self.message
        return self.__class__.__name__

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"{self.message!r}, status_code={self.status_code})"
        )
