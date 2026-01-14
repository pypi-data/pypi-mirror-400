"""Bulk insert request DTOs."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class NodeData(BaseModel):
    """Node data for bulk insert."""

    labels: list[str] = Field(..., min_length=1)
    properties: dict[str, Any]


class RelationshipData(BaseModel):
    """Relationship data for bulk insert."""

    type: str = Field(..., min_length=1)
    start_node: dict[str, int]  # {"id": node_id}
    end_node: dict[str, int]  # {"id": node_id}
    properties: dict[str, Any] = Field(default_factory=dict)


class BulkInsertRequest(BaseModel):
    """Bulk insert nodes and relationships."""

    alias: str | None = None
    neo4j_uri: str | None = None
    nodes: list[NodeData] = Field(default_factory=list)
    relationships: list[RelationshipData] = Field(default_factory=list)
