"""Admin request DTOs."""

from __future__ import annotations

from pydantic import BaseModel


class Neo4jCredentialsRequest(BaseModel):
    """Store Neo4j credentials."""

    uri: str
    username: str
    password: str
    database: str | None = None
    alias: str | None = None


class ApiKeyCreateRequest(BaseModel):
    """Create scoped API key."""

    name: str
    allowed_aliases: list[str]


class ApiKeyUpdateRequest(BaseModel):
    """Update API key permissions."""

    allowed_aliases: list[str]
