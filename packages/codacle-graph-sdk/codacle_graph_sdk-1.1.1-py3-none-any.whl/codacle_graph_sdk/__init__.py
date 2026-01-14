"""Codacle Graph SDK - Python client for Codacle Graph Service."""

from importlib.metadata import version

__version__ = version("codacle-graph-sdk")
from .clients import AsyncClient, Client
from .exceptions import (
    AuthenticationError,
    CodacleGraphError,
    ConflictError,
    ForbiddenError,
    InputValidationError,
    LLMServiceError,
    Neo4jQueryError,
    NetworkError,
    NotFoundError,
    ServerError,
    TranslationError,
    ValidationError,
)
from .models._base import BaseNode, BaseRelationship, Metadata, NodeReference
from .models.nodes import (
    ApplicationNode,
    AttributeNode,
    ClassNode,
    ClientNode,
    ModuleNode,
    NodeType,
    ObjectNode,
    SubroutineNode,
    parse_node,
)
from .models.relationships import (
    Contains,
    ContainsImports,
    CreatesInstance,
    DefinesAttribute,
    DefinesMethod,
    HasApplication,
    HasClass,
    HasInstance,
    HasMethod,
    HasModule,
    HasSubroutine,
    InheritsFrom,
    InstantiatesClass,
    Refers,
    RelationshipType,
    Triggers,
    Uses,
    parse_relationship,
)
from .models.requests import BulkInsertRequest, NodeData, RelationshipData
from .models.responses import (
    BulkInsertResponse,
    CypherQueryResponse,
)

# Backward compatibility aliases
CodacleGraphClient = Client
AsyncCodacleGraphClient = AsyncClient

__all__ = [
    # Version
    "__version__",
    # Clients (new names)
    "Client",
    "AsyncClient",
    # Clients (backward compatibility)
    "CodacleGraphClient",
    "AsyncCodacleGraphClient",
    # Base models
    "BaseNode",
    "BaseRelationship",
    "Metadata",
    "NodeReference",
    # Node types
    "ClientNode",
    "ApplicationNode",
    "ModuleNode",
    "ClassNode",
    "SubroutineNode",
    "AttributeNode",
    "ObjectNode",
    "NodeType",
    "parse_node",
    # Relationship types
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
    "parse_relationship",
    # Request helpers
    "NodeData",
    "RelationshipData",
    "BulkInsertRequest",
    # Responses
    "CypherQueryResponse",
    "BulkInsertResponse",
    # Exceptions
    "CodacleGraphError",
    "AuthenticationError",
    "ForbiddenError",
    "NetworkError",
    "NotFoundError",
    "ValidationError",
    "InputValidationError",
    "ConflictError",
    "Neo4jQueryError",
    "TranslationError",
    "LLMServiceError",
    "ServerError",
]
