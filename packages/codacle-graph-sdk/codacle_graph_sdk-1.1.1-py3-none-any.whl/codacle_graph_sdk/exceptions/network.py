"""Network-related exceptions."""

from __future__ import annotations

from ._base import CodacleGraphError


class NetworkError(CodacleGraphError):
    """Network-related errors (timeout, connection failed)."""

    pass
