"""Node type models."""

from __future__ import annotations

from typing import Any

from .._base import BaseNode
from .application import ApplicationNode
from .attribute import AttributeNode
from .class_ import ClassNode
from .client import ClientNode
from .module import ModuleNode
from .object import ObjectNode
from .subroutine import SubroutineNode

__all__ = [
    "BaseNode",
    "ClientNode",
    "ApplicationNode",
    "ModuleNode",
    "ClassNode",
    "SubroutineNode",
    "AttributeNode",
    "ObjectNode",
    "NodeType",
    "NODE_TYPE_MAP",
    "parse_node",
]

# Type alias for all node types
NodeType = (
    ClientNode
    | ApplicationNode
    | ModuleNode
    | ClassNode
    | SubroutineNode
    | AttributeNode
    | ObjectNode
)

# Mapping for dynamic node construction
NODE_TYPE_MAP: dict[str, type[BaseNode]] = {
    "Client": ClientNode,
    "Application": ApplicationNode,
    "Module": ModuleNode,
    "Class": ClassNode,
    "Subroutine": SubroutineNode,
    "Attribute": AttributeNode,
    "Object": ObjectNode,
}


def _infer_node_type_from_path(path: str) -> str | None:
    """Infer node type from path string."""
    path_lower = path.lower()
    if "/class:" in path_lower or path_lower.startswith("class:"):
        return "Class"
    if "/module:" in path_lower or path_lower.startswith("module:"):
        return "Module"
    if "/subroutine:" in path_lower or path_lower.startswith("subroutine:"):
        return "Subroutine"
    if "/method:" in path_lower or path_lower.startswith("method:"):
        return "Subroutine"
    if "/object:" in path_lower or path_lower.startswith("object:"):
        return "Object"
    if "/attribute:" in path_lower or path_lower.startswith("attribute:"):
        return "Attribute"
    return None


def _infer_node_type_from_properties(data: dict[str, Any]) -> str | None:
    """Infer node type from node properties."""
    if "is_abstract" in data or "is_interface" in data or "bases" in data:
        return "Class"
    if "signature" in data or "is_async" in data or "return_type" in data:
        return "Subroutine"
    if "type_annotation" in data or "default_value" in data:
        return "Attribute"
    if "className" in data or "class_name" in data:
        return "Object"
    path = data.get("path", "")
    if path:
        inferred = _infer_node_type_from_path(path)
        if inferred:
            return inferred
    if data.get("type") == "Folder":
        return "Module"
    return None


def parse_node(data: dict[str, Any]) -> BaseNode:
    """Parse Neo4j node data into typed node instance.

    Handles both Neo4j format (with labels/identity) and raw property dicts.
    """
    labels = data.get("labels", [])
    for label in labels:
        if label in NODE_TYPE_MAP:
            return NODE_TYPE_MAP[label].from_neo4j(data)

    inferred_type = _infer_node_type_from_properties(data)
    if inferred_type and inferred_type in NODE_TYPE_MAP:
        node_class = NODE_TYPE_MAP[inferred_type]
        props = data.get("properties", data)
        return node_class(
            id=data.get("identity") or data.get("id"),
            name=props.get("name", ""),
            metadata={k: v for k, v in props.items() if k != "name"},
        )

    return BaseNode.from_neo4j(data)
