"""Synchronous Codacle Graph SDK client."""

from __future__ import annotations

from typing import Any

from .._core._http import HttpClient
from ..models.nodes import (
    ApplicationNode,
    AttributeNode,
    ClassNode,
    ClientNode,
    ModuleNode,
    ObjectNode,
    SubroutineNode,
)
from ..models.requests import (
    ApiKeyCreateRequest,
    ApiKeyUpdateRequest,
    BulkInsertRequest,
    CypherQueryRequest,
    NaturalQueryRequest,
    Neo4jCredentialsRequest,
    NodeData,
    QueryMappingRequest,
    RelationshipData,
)
from ..models.responses import (
    ApiKeyCreateResponse,
    ApiKeyListResponse,
    ApiKeyUpdateResponse,
    BulkInsertResponse,
    CredentialSaveResponse,
    CypherQueryResponse,
    DeleteResponse,
    DriverPoolStats,
    HealthResponse,
    NaturalQueryResponse,
    Neo4jCredentialsResponse,
    QueryMapping,
    QueryMappingCreateResponse,
    QueryMappingResponse,
    QueryMappingsResponse,
)


def _escape_cypher_string(value: str) -> str:
    """Escape special characters for Cypher string literals."""
    return value.replace("\\", "\\\\").replace("'", "\\'")


class Client:
    """
    Synchronous client for Codacle Graph Service.

    Args:
        url: Base URL of the Codacle Graph Service.
        api_key: API key for authentication.
        alias: Default Neo4j instance alias (optional).
        timeout: Request timeout in seconds (default: 30).

    Example:
        >>> client = Client(
        ...     url="https://api.codacle.com",
        ...     api_key="your-api-key",
        ...     alias="production-db",
        ... )
        >>> result = client.natural_query("Find all classes")
        >>> for node in result.get_nodes():
        ...     print(node.name)
    """

    def __init__(
        self,
        url: str,
        api_key: str,
        alias: str | None = None,
        timeout: float = 30.0,
    ):
        self._http = HttpClient(url, api_key, timeout)
        self._default_alias = alias

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        self._http.close()

    def _resolve_alias(self, alias: str | None) -> str | None:
        """Use provided alias or fall back to default."""
        return alias if alias is not None else self._default_alias

    # -------------------------------------------------------------------------
    # Query Operations
    # -------------------------------------------------------------------------

    def natural_query(
        self,
        query: str,
        alias: str | None = None,
        neo4j_uri: str | None = None,
    ) -> NaturalQueryResponse:
        """
        Execute natural language query (translated to Cypher via LLM).

        Args:
            query: Natural language question.
            alias: Neo4j instance alias (uses default if not provided).
            neo4j_uri: Direct Neo4j URI (overrides alias).

        Returns:
            Query response with results and generated Cypher.

        Raises:
            TranslationError: LLM translation failed.
            Neo4jQueryError: Query execution failed.
        """
        data = self._http.post(
            "/api/v1/natural-query",
            json=NaturalQueryRequest(
                query=query,
                alias=self._resolve_alias(alias),
                neo4j_uri=neo4j_uri,
            ).model_dump(exclude_none=True),
        )
        return NaturalQueryResponse.model_validate(data)

    def cypher_query(
        self,
        query: str,
        alias: str | None = None,
        neo4j_uri: str | None = None,
    ) -> CypherQueryResponse:
        """
        Execute Cypher query, stored query (by name/ID), or natural language.

        Args:
            query: Cypher query, stored query name/ID, or natural language.
            alias: Neo4j instance alias.
            neo4j_uri: Direct Neo4j URI.

        Returns:
            Query response with results.
        """
        data = self._http.post(
            "/api/v1/cypher-query",
            json=CypherQueryRequest(
                query=query,
                alias=self._resolve_alias(alias),
                neo4j_uri=neo4j_uri,
            ).model_dump(exclude_none=True),
        )
        return CypherQueryResponse.model_validate(data)

    # -------------------------------------------------------------------------
    # Query Mappings
    # -------------------------------------------------------------------------

    def list_query_mappings(self) -> list[QueryMapping]:
        """List all stored query mappings."""
        data = self._http.get("/api/v1/query-mappings")
        return QueryMappingsResponse.model_validate(data).mappings

    def get_query_mapping(self, identifier: str) -> QueryMapping:
        """
        Get query mapping by ID or name.

        Args:
            identifier: MongoDB ObjectID or mapping name.

        Raises:
            NotFoundError: Mapping not found.
        """
        data = self._http.get(f"/api/v1/query-mapping/{identifier}")
        return QueryMappingResponse.model_validate(data).details

    def create_query_mapping(
        self,
        name: str,
        natural_language_query: str,
        cypher_query: str,
    ) -> QueryMappingCreateResponse:
        """
        Create or update a query mapping.

        Args:
            name: Unique name (or MongoDB ID for updates).
            natural_language_query: The natural language question.
            cypher_query: The corresponding Cypher query.

        Returns:
            Response with name, action (created/updated), and counts.
        """
        data = self._http.post(
            "/api/v1/query-mapping",
            json=QueryMappingRequest(
                name=name,
                natural_language_query=natural_language_query,
                cypher_query=cypher_query,
            ).model_dump(),
        )
        return QueryMappingCreateResponse.model_validate(data)

    def delete_query_mapping(self, identifier: str) -> DeleteResponse:
        """Delete query mapping by ID or name."""
        data = self._http.delete(f"/api/v1/query-mapping/{identifier}")
        return DeleteResponse.model_validate(data)

    # -------------------------------------------------------------------------
    # Bulk Operations
    # -------------------------------------------------------------------------

    def bulk_insert(
        self,
        nodes: list[NodeData] | None = None,
        relationships: list[RelationshipData] | None = None,
        alias: str | None = None,
        neo4j_uri: str | None = None,
    ) -> BulkInsertResponse:
        """
        Bulk insert nodes and/or relationships.

        Args:
            nodes: List of nodes to create.
            relationships: List of relationships to create.
            alias: Neo4j instance alias.
            neo4j_uri: Direct Neo4j URI.
        """
        data = self._http.post(
            "/api/v1/bulk-insert",
            json=BulkInsertRequest(
                alias=self._resolve_alias(alias),
                neo4j_uri=neo4j_uri,
                nodes=nodes or [],
                relationships=relationships or [],
            ).model_dump(exclude_none=True),
        )
        return BulkInsertResponse.model_validate(data)

    # -------------------------------------------------------------------------
    # Admin: Neo4j Credentials (requires admin API key)
    # -------------------------------------------------------------------------

    def list_credentials(self) -> Neo4jCredentialsResponse:
        """List all Neo4j credentials (admin only)."""
        data = self._http.get("/api/v1/neo4j-credentials")
        return Neo4jCredentialsResponse.model_validate(data)

    def add_credentials(
        self,
        uri: str,
        username: str,
        password: str,
        database: str | None = None,
        alias: str | None = None,
    ) -> CredentialSaveResponse:
        """Store Neo4j credentials (admin only)."""
        data = self._http.post(
            "/api/v1/neo4j-credentials",
            json=Neo4jCredentialsRequest(
                uri=uri,
                username=username,
                password=password,
                database=database,
                alias=alias,
            ).model_dump(exclude_none=True),
        )
        return CredentialSaveResponse.model_validate(data)

    # -------------------------------------------------------------------------
    # Admin: API Keys (requires admin API key)
    # -------------------------------------------------------------------------

    def create_api_key(
        self,
        name: str,
        allowed_aliases: list[str],
    ) -> ApiKeyCreateResponse:
        """Create scoped API key (admin only)."""
        data = self._http.post(
            "/api/v1/permissions",
            json=ApiKeyCreateRequest(
                name=name,
                allowed_aliases=allowed_aliases,
            ).model_dump(),
        )
        return ApiKeyCreateResponse.model_validate(data)

    def list_api_keys(self) -> ApiKeyListResponse:
        """List all API keys (admin only)."""
        data = self._http.get("/api/v1/permissions")
        return ApiKeyListResponse.model_validate(data)

    def update_api_key(
        self,
        identifier: str,
        allowed_aliases: list[str],
    ) -> ApiKeyUpdateResponse:
        """Update API key permissions (admin only)."""
        data = self._http.put(
            f"/api/v1/permissions/{identifier}",
            json=ApiKeyUpdateRequest(
                allowed_aliases=allowed_aliases
            ).model_dump(),
        )
        return ApiKeyUpdateResponse.model_validate(data)

    def delete_api_key(self, identifier: str) -> DeleteResponse:
        """Revoke API key (admin only)."""
        data = self._http.delete(f"/api/v1/permissions/{identifier}")
        return DeleteResponse.model_validate(data)

    # -------------------------------------------------------------------------
    # Monitoring
    # -------------------------------------------------------------------------

    def health(self) -> HealthResponse:
        """Check service health (no auth required)."""
        data = self._http.get("/health")
        return HealthResponse.model_validate(data)

    def driver_pool_stats(self) -> DriverPoolStats:
        """Get Neo4j driver pool statistics (admin only)."""
        data = self._http.get("/api/v1/driver-pool-stats")
        return DriverPoolStats.model_validate(data)

    # -------------------------------------------------------------------------
    # Convenience Methods - Graph Traversals
    # -------------------------------------------------------------------------

    def get_clients(self, alias: str | None = None) -> list[ClientNode]:
        """Get all Client nodes."""
        result = self.cypher_query("MATCH (c:Client) RETURN c", alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ClientNode)]

    def get_applications(
        self,
        client_name: str | None = None,
        alias: str | None = None,
    ) -> list[ApplicationNode]:
        """
        Get Application nodes, optionally filtered by client.

        Args:
            client_name: Filter by parent client name.
        """
        if client_name:
            escaped = _escape_cypher_string(client_name)
            query = (
                f"MATCH (c:Client {{name: '{escaped}'}})"
                "-[:has_application]->(a:Application) RETURN a"
            )
        else:
            query = "MATCH (a:Application) RETURN a"
        result = self.cypher_query(query, alias=alias)
        return [
            n for n in result.get_nodes() if isinstance(n, ApplicationNode)
        ]

    def get_modules(
        self,
        application_name: str | None = None,
        alias: str | None = None,
    ) -> list[ModuleNode]:
        """Get Module nodes, optionally filtered by application."""
        if application_name:
            escaped = _escape_cypher_string(application_name)
            query = (
                f"MATCH (app:Application {{name: '{escaped}'}})"
                "-[:has_module]->(m:Module) RETURN m"
            )
        else:
            query = "MATCH (m:Module) RETURN m"
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ModuleNode)]

    def get_classes_in_module(
        self,
        module_name: str,
        alias: str | None = None,
    ) -> list[ClassNode]:
        """Get all classes defined in a module."""
        escaped = _escape_cypher_string(module_name)
        query = (
            f"MATCH (m:Module {{name: '{escaped}'}})"
            "-[:has_class]->(c:Class) RETURN c"
        )
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ClassNode)]

    def get_methods_of_class(
        self,
        class_name: str,
        alias: str | None = None,
    ) -> list[SubroutineNode]:
        """Get all methods defined in a class."""
        escaped = _escape_cypher_string(class_name)
        query = (
            f"MATCH (c:Class {{name: '{escaped}'}})"
            "-[:defines_method]->(s:Subroutine) RETURN s"
        )
        result = self.cypher_query(query, alias=alias)
        nodes = result.get_nodes()
        return [n for n in nodes if isinstance(n, SubroutineNode)]

    def get_attributes_of_class(
        self,
        class_name: str,
        alias: str | None = None,
    ) -> list[AttributeNode]:
        """Get all attributes defined in a class."""
        escaped = _escape_cypher_string(class_name)
        query = (
            f"MATCH (c:Class {{name: '{escaped}'}})"
            "-[:defines_attribute]->(a:Attribute) RETURN a"
        )
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, AttributeNode)]

    def get_class_hierarchy(
        self,
        class_name: str,
        alias: str | None = None,
    ) -> list[ClassNode]:
        """Get inheritance chain (parents) of a class."""
        escaped = _escape_cypher_string(class_name)
        query = (
            f"MATCH (c:Class {{name: '{escaped}'}})"
            "-[:inherits_from*]->(parent:Class) RETURN parent"
        )
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ClassNode)]

    def get_subroutines_in_module(
        self,
        module_name: str,
        alias: str | None = None,
    ) -> list[SubroutineNode]:
        """Get all functions/subroutines in a module."""
        escaped = _escape_cypher_string(module_name)
        query = (
            f"MATCH (m:Module {{name: '{escaped}'}})"
            "-[:has_subroutine]->(s:Subroutine) RETURN s"
        )
        result = self.cypher_query(query, alias=alias)
        nodes = result.get_nodes()
        return [n for n in nodes if isinstance(n, SubroutineNode)]

    def get_module_imports(
        self,
        module_name: str,
        alias: str | None = None,
    ) -> list[ModuleNode]:
        """Get modules imported by a module."""
        escaped = _escape_cypher_string(module_name)
        query = (
            f"MATCH (m:Module {{name: '{escaped}'}})"
            "-[:contains_imports]->(imported:Module) RETURN imported"
        )
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ModuleNode)]

    def get_callers_of_subroutine(
        self,
        subroutine_name: str,
        alias: str | None = None,
    ) -> list[SubroutineNode]:
        """Get subroutines that trigger/call this subroutine."""
        escaped = _escape_cypher_string(subroutine_name)
        query = (
            f"MATCH (caller:Subroutine)-[:triggers]->"
            f"(s:Subroutine {{name: '{escaped}'}}) RETURN caller"
        )
        result = self.cypher_query(query, alias=alias)
        nodes = result.get_nodes()
        return [n for n in nodes if isinstance(n, SubroutineNode)]

    def get_objects_used_by_subroutine(
        self,
        subroutine_name: str,
        alias: str | None = None,
    ) -> list[ObjectNode]:
        """Get objects used by a subroutine."""
        escaped = _escape_cypher_string(subroutine_name)
        query = (
            f"MATCH (s:Subroutine {{name: '{escaped}'}})"
            "-[:uses]->(o:Object) RETURN o"
        )
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ObjectNode)]

    def get_instances_of_class(
        self,
        class_name: str,
        alias: str | None = None,
    ) -> list[ObjectNode]:
        """Get all object instances of a class."""
        escaped = _escape_cypher_string(class_name)
        query = (
            f"MATCH (c:Class {{name: '{escaped}'}})"
            "-[:has_instance]->(o:Object) RETURN o"
        )
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ObjectNode)]

    def get_subclasses(
        self,
        class_name: str,
        alias: str | None = None,
    ) -> list[ClassNode]:
        """Get classes that inherit from this class."""
        escaped = _escape_cypher_string(class_name)
        query = (
            f"MATCH (child:Class)-[:inherits_from]->"
            f"(c:Class {{name: '{escaped}'}}) RETURN child"
        )
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ClassNode)]

    def get_full_module_structure(
        self,
        module_name: str,
        alias: str | None = None,
    ) -> dict[str, Any]:
        """
        Get complete module structure with classes, functions, imports.

        Returns dict with keys: 'classes', 'subroutines', 'imports'.
        """
        return {
            "classes": self.get_classes_in_module(module_name, alias),
            "subroutines": self.get_subroutines_in_module(module_name, alias),
            "imports": self.get_module_imports(module_name, alias),
        }

    def get_full_class_structure(
        self,
        class_name: str,
        alias: str | None = None,
    ) -> dict[str, Any]:
        """
        Get complete class structure with methods, attributes, hierarchy.

        Returns dict with keys: 'methods', 'attributes', 'parents',
        'children', 'instances'.
        """
        return {
            "methods": self.get_methods_of_class(class_name, alias),
            "attributes": self.get_attributes_of_class(class_name, alias),
            "parents": self.get_class_hierarchy(class_name, alias),
            "children": self.get_subclasses(class_name, alias),
            "instances": self.get_instances_of_class(class_name, alias),
        }
