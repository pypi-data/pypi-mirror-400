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
    """Infer node type from path string.

    Finds the LAST (most specific) type indicator in the path.
    E.g., 'client:Axoft/module:foo/class:Bar' -> 'Class'
    """
    path_lower = path.lower()

    # Type prefixes in order of specificity (most specific first for matching)
    type_prefixes = [
        ("attribute:", "Attribute"),
        ("object:", "Object"),
        ("subroutine:", "Subroutine"),
        ("method:", "Subroutine"),
        ("class:", "Class"),
        ("module:", "Module"),
        ("application:", "Application"),
        ("client:", "Client"),
    ]

    # Find the rightmost (most specific) type indicator
    last_match = None
    last_pos = -1

    for prefix, node_type in type_prefixes:
        # Find the last occurrence of this prefix
        pos = path_lower.rfind(prefix)
        if pos > last_pos:
            last_pos = pos
            last_match = node_type

    return last_match


def _infer_node_type_from_properties(data: dict[str, Any]) -> str | None:
    """Infer node type from node properties."""
    # Get properties (may be nested or at top level)
    props = data.get("properties", data)

    # Check path first - most reliable source
    path = (
        props.get("path", "")
        or props.get("symbol_path", "")
        or data.get("path", "")
        or data.get("symbol_path", "")
    )
    if path:
        inferred = _infer_node_type_from_path(path)
        if inferred:
            return inferred

    # Check for type field (common in Client/Application)
    node_type = props.get("type", "") or data.get("type", "")
    if node_type in ("Organization", "Company", "Client"):
        return "Client"
    if node_type in ("Application", "App", "Project"):
        return "Application"

    # Check for specific properties (check both levels)
    all_keys = set(props.keys()) | set(data.keys())
    class_indicators = {"is_abstract", "is_interface", "bases"}
    if class_indicators & all_keys:
        return "Class"
    sub_indicators = {"signature", "is_async", "return_type"}
    if sub_indicators & all_keys:
        return "Subroutine"
    if "type_annotation" in all_keys or "default_value" in all_keys:
        return "Attribute"
    if "className" in all_keys or "class_name" in all_keys:
        return "Object"
    if node_type == "Folder":
        return "Module"
    return None


# Priority order for label matching (most specific first)
LABEL_PRIORITY = [
    "Client",
    "Application",
    "Class",
    "Subroutine",
    "Attribute",
    "Object",
    "Module",  # Module is least specific (often combined with others)
]


def parse_node(data: dict[str, Any]) -> BaseNode:
    """Parse Neo4j node data into typed node instance.

    Handles both Neo4j format (with labels/identity) and raw property dicts.
    """
    labels = set(data.get("labels", []))

    # Check labels in priority order (most specific first)
    for label in LABEL_PRIORITY:
        if label in labels and label in NODE_TYPE_MAP:
            return NODE_TYPE_MAP[label].from_neo4j(data)

    # Fallback: check any remaining labels
    for label in labels:
        if label in NODE_TYPE_MAP:
            return NODE_TYPE_MAP[label].from_neo4j(data)

    # Try to infer from properties/path
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
