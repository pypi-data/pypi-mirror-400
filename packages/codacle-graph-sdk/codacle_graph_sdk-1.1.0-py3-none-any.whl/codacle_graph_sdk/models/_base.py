"""Base models for graph entities."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

Metadata = dict[str, Any]


class BaseNode(BaseModel):
    """Base class for all Neo4j nodes."""

    model_config = ConfigDict(extra="allow", frozen=False)

    id: int | None = Field(None, description="Neo4j internal node ID")
    name: str = Field(..., description="Unique name identifier")
    metadata: Metadata = Field(
        default_factory=dict, description="Dynamic metadata"
    )

    @classmethod
    def from_neo4j(cls, data: dict[str, Any]) -> BaseNode:
        """Construct node from Neo4j result dict."""
        props = data.get("properties", data)
        return cls(
            id=data.get("identity") or data.get("id"),
            name=props.get("name", ""),
            metadata={k: v for k, v in props.items() if k not in ("name",)},
        )


class BaseRelationship(BaseModel):
    """Base class for all Neo4j relationships."""

    model_config = ConfigDict(extra="allow", frozen=False)

    id: int | None = Field(
        None, description="Neo4j internal relationship ID"
    )
    start_node_id: int = Field(..., description="Source node ID")
    end_node_id: int = Field(..., description="Target node ID")
    properties: Metadata = Field(default_factory=dict)

    @classmethod
    def from_neo4j(cls, data: dict[str, Any]) -> BaseRelationship:
        """Construct relationship from Neo4j result dict."""
        start = data.get("start") or data.get("start_node_id") or 0
        end = data.get("end") or data.get("end_node_id") or 0
        return cls(
            id=data.get("identity") or data.get("id"),
            start_node_id=start,
            end_node_id=end,
            properties=data.get("properties", {}),
        )


class NodeReference(BaseModel):
    """Reference to a node by ID (for relationship endpoints)."""

    id: int
