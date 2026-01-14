"""Query request DTOs."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from codacle_graph_sdk._core._validation import (
    validate_alias,
    validate_query_string,
)


class CypherQueryRequest(BaseModel):
    """Direct Cypher query request."""

    query: str = Field(
        ...,
        min_length=1,
        description="Cypher query, stored query name, or MongoDB ID",
    )
    alias: str | None = None
    neo4j_uri: str | None = None

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        return validate_query_string(v, allow_empty=False)

    @field_validator("alias")
    @classmethod
    def validate_alias_field(cls, v: str | None) -> str | None:
        return validate_alias(v)
