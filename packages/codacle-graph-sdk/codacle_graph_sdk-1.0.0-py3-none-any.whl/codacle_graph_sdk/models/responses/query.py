"""Query response DTOs."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator

from .._base import BaseNode, BaseRelationship
from ..nodes import parse_node
from ..relationships import parse_relationship
from ._utils import parse_mongo_oid


class QueryDetails(BaseModel):
    """Query execution details."""

    id: str | None = Field(None, alias="_id")
    name: str | None = None
    natural_language_query: str | None = None
    cypher_query: str

    @field_validator("id", mode="before")
    @classmethod
    def parse_id(cls, v: Any) -> str | None:
        return parse_mongo_oid(v)


def _is_node_like(value: dict[str, Any]) -> bool:
    """Check if dict looks like a node (has labels or name/path)."""
    if "labels" in value:
        return True
    if "name" in value and ("path" in value or "type" in value):
        return True
    return False


class NaturalQueryResponse(BaseModel):
    """Response from natural language query."""

    query: str | None = None
    query_details: QueryDetails | None = None
    results: list[dict[str, Any]]
    source: str  # "translation" | "stored_query"

    def get_nodes(self) -> list[BaseNode]:
        """Extract and parse all nodes from results."""
        nodes = []
        for record in self.results:
            for value in record.values():
                if isinstance(value, dict) and _is_node_like(value):
                    nodes.append(parse_node(value))
        return nodes

    def get_relationships(self) -> list[BaseRelationship]:
        """Extract and parse all relationships from results."""
        rels = []
        for record in self.results:
            for value in record.values():
                if (
                    isinstance(value, dict)
                    and "type" in value
                    and "start" in value
                ):
                    rels.append(parse_relationship(value))
        return rels


class CypherQueryResponse(BaseModel):
    """Response from Cypher query."""

    query_details: QueryDetails
    results: list[dict[str, Any]]
    source: str  # "stored_query" | "direct_query"

    def get_nodes(self) -> list[BaseNode]:
        """Extract and parse all nodes from results."""
        nodes = []
        for record in self.results:
            for value in record.values():
                if isinstance(value, dict) and _is_node_like(value):
                    nodes.append(parse_node(value))
        return nodes
