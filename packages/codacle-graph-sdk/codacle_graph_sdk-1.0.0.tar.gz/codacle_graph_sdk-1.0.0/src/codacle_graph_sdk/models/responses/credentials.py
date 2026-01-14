"""Credentials response DTOs."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator

from ._utils import parse_mongo_oid


class CredentialInfo(BaseModel):
    """Neo4j credential info (password masked)."""

    id: str | None = Field(None, alias="_id")
    uri: str
    username: str
    password: str  # Masked
    database: str | None = None
    alias: str | None = None

    @field_validator("id", mode="before")
    @classmethod
    def parse_id(cls, v: Any) -> str | None:
        return parse_mongo_oid(v)


class Neo4jCredentialsResponse(BaseModel):
    """List of Neo4j credentials."""

    credentials: list[CredentialInfo]


class CredentialSaveResponse(BaseModel):
    """Credential save result."""

    message: str
    details: dict[str, Any]
