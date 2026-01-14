"""Relationship type models."""

from __future__ import annotations

from typing import Any

from .._base import BaseRelationship
from .hierarchy import HasApplication, HasClass, HasModule, HasSubroutine
from .inheritance import InheritsFrom
from .instance import CreatesInstance, HasInstance, InstantiatesClass
from .references import Contains, HasMethod, Refers, Triggers, Uses
from .structure import ContainsImports, DefinesAttribute, DefinesMethod

__all__ = [
    "BaseRelationship",
    "HasApplication",
    "HasModule",
    "HasSubroutine",
    "HasClass",
    "ContainsImports",
    "DefinesAttribute",
    "CreatesInstance",
    "InheritsFrom",
    "DefinesMethod",
    "HasInstance",
    "HasMethod",
    "Contains",
    "Uses",
    "InstantiatesClass",
    "Refers",
    "Triggers",
    "RelationshipType",
    "RELATIONSHIP_TYPE_MAP",
    "parse_relationship",
]

# Type alias for all relationship types
RelationshipType = (
    HasApplication
    | HasModule
    | HasSubroutine
    | HasClass
    | ContainsImports
    | DefinesAttribute
    | CreatesInstance
    | InheritsFrom
    | DefinesMethod
    | HasInstance
    | HasMethod
    | Contains
    | Uses
    | InstantiatesClass
    | Refers
    | Triggers
)

RELATIONSHIP_TYPE_MAP: dict[str, type[BaseRelationship]] = {
    "has_application": HasApplication,
    "has_module": HasModule,
    "has_subroutine": HasSubroutine,
    "has_class": HasClass,
    "contains_imports": ContainsImports,
    "defines_attribute": DefinesAttribute,
    "creates_instance": CreatesInstance,
    "inherits_from": InheritsFrom,
    "defines_method": DefinesMethod,
    "has_instance": HasInstance,
    "has_method": HasMethod,
    "contains": Contains,
    "uses": Uses,
    "instantiates_class": InstantiatesClass,
    "refers": Refers,
    "triggers": Triggers,
}


def parse_relationship(data: dict[str, Any]) -> BaseRelationship:
    """Parse Neo4j relationship data into typed instance."""
    rel_type = data.get("type", "").lower()
    if rel_type in RELATIONSHIP_TYPE_MAP:
        return RELATIONSHIP_TYPE_MAP[rel_type].from_neo4j(data)
    return BaseRelationship.from_neo4j(data)
