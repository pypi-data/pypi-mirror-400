"""Query mapping response DTOs."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator

from ._utils import parse_mongo_oid


class QueryMapping(BaseModel):
    """Stored query mapping."""

    id: str = Field(..., alias="_id")
    name: str
    natural_language_query: str
    cypher_query: str

    @field_validator("id", mode="before")
    @classmethod
    def parse_id(cls, v: Any) -> str:
        result = parse_mongo_oid(v)
        return result or ""


class QueryMappingsResponse(BaseModel):
    """List of query mappings."""

    mappings: list[QueryMapping]


class QueryMappingResponse(BaseModel):
    """Single query mapping response (GET)."""

    message: str
    details: QueryMapping


class QueryMappingCreateResponse(BaseModel):
    """Response from creating/updating a query mapping."""

    name: str
    action: str  # "inserted" | "updated"
    matched_count: int = 0
    modified_count: int = 0
