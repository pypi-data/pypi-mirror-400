"""Query request DTOs."""

from __future__ import annotations

from pydantic import BaseModel, Field


class NaturalQueryRequest(BaseModel):
    """Natural language query request."""

    query: str = Field(..., description="Natural language question")
    alias: str | None = Field(None, description="Neo4j instance alias")
    neo4j_uri: str | None = Field(None, description="Direct Neo4j URI")


class CypherQueryRequest(BaseModel):
    """Direct Cypher query request."""

    query: str = Field(
        ..., description="Cypher query, stored query name, or MongoDB ID"
    )
    alias: str | None = None
    neo4j_uri: str | None = None


class QueryMappingRequest(BaseModel):
    """Create/update query mapping."""

    name: str = Field(..., description="Unique name for the mapping")
    natural_language_query: str
    cypher_query: str
