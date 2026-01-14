"""Asynchronous Codacle Graph SDK client."""

from __future__ import annotations

from typing import Any

from .._core._http import AsyncHttpClient
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


class AsyncClient:
    """
    Asynchronous client for Codacle Graph Service.

    Args:
        url: Base URL of the Codacle Graph Service.
        api_key: API key for authentication.
        alias: Default Neo4j instance alias (optional).
        timeout: Request timeout in seconds (default: 30).

    Example:
        >>> async with AsyncClient(
        ...     url="https://api.codacle.com",
        ...     api_key="your-api-key",
        ...     alias="production-db",
        ... ) as client:
        ...     result = await client.natural_query("Find all classes")
        ...     for node in result.get_nodes():
        ...         print(node.name)
    """

    def __init__(
        self,
        url: str,
        api_key: str,
        alias: str | None = None,
        timeout: float = 30.0,
    ):
        self._http = AsyncHttpClient(url, api_key, timeout)
        self._default_alias = alias

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._http.close()

    def _resolve_alias(self, alias: str | None) -> str | None:
        return alias if alias is not None else self._default_alias

    # -------------------------------------------------------------------------
    # Query Operations
    # -------------------------------------------------------------------------

    async def natural_query(
        self,
        query: str,
        alias: str | None = None,
        neo4j_uri: str | None = None,
    ) -> NaturalQueryResponse:
        """Execute natural language query."""
        data = await self._http.post(
            "/api/v1/natural-query",
            json=NaturalQueryRequest(
                query=query,
                alias=self._resolve_alias(alias),
                neo4j_uri=neo4j_uri,
            ).model_dump(exclude_none=True),
        )
        return NaturalQueryResponse.model_validate(data)

    async def cypher_query(
        self,
        query: str,
        alias: str | None = None,
        neo4j_uri: str | None = None,
    ) -> CypherQueryResponse:
        """Execute Cypher query."""
        data = await self._http.post(
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

    async def list_query_mappings(self) -> list[QueryMapping]:
        """List all stored query mappings."""
        data = await self._http.get("/api/v1/query-mappings")
        return QueryMappingsResponse.model_validate(data).mappings

    async def get_query_mapping(self, identifier: str) -> QueryMapping:
        """Get query mapping by ID or name."""
        data = await self._http.get(f"/api/v1/query-mapping/{identifier}")
        return QueryMappingResponse.model_validate(data).details

    async def create_query_mapping(
        self,
        name: str,
        natural_language_query: str,
        cypher_query: str,
    ) -> QueryMappingCreateResponse:
        """Create or update query mapping."""
        data = await self._http.post(
            "/api/v1/query-mapping",
            json=QueryMappingRequest(
                name=name,
                natural_language_query=natural_language_query,
                cypher_query=cypher_query,
            ).model_dump(),
        )
        return QueryMappingCreateResponse.model_validate(data)

    async def delete_query_mapping(self, identifier: str) -> DeleteResponse:
        """Delete query mapping."""
        data = await self._http.delete(f"/api/v1/query-mapping/{identifier}")
        return DeleteResponse.model_validate(data)

    # -------------------------------------------------------------------------
    # Bulk Operations
    # -------------------------------------------------------------------------

    async def bulk_insert(
        self,
        nodes: list[NodeData] | None = None,
        relationships: list[RelationshipData] | None = None,
        alias: str | None = None,
        neo4j_uri: str | None = None,
    ) -> BulkInsertResponse:
        """Bulk insert nodes and relationships."""
        data = await self._http.post(
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

    async def list_credentials(self) -> Neo4jCredentialsResponse:
        """List Neo4j credentials (admin only)."""
        data = await self._http.get("/api/v1/neo4j-credentials")
        return Neo4jCredentialsResponse.model_validate(data)

    async def add_credentials(
        self,
        uri: str,
        username: str,
        password: str,
        database: str | None = None,
        alias: str | None = None,
    ) -> CredentialSaveResponse:
        """Store Neo4j credentials (admin only)."""
        data = await self._http.post(
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

    async def create_api_key(
        self,
        name: str,
        allowed_aliases: list[str],
    ) -> ApiKeyCreateResponse:
        """Create scoped API key (admin only)."""
        data = await self._http.post(
            "/api/v1/permissions",
            json=ApiKeyCreateRequest(
                name=name,
                allowed_aliases=allowed_aliases,
            ).model_dump(),
        )
        return ApiKeyCreateResponse.model_validate(data)

    async def list_api_keys(self) -> ApiKeyListResponse:
        """List API keys (admin only)."""
        data = await self._http.get("/api/v1/permissions")
        return ApiKeyListResponse.model_validate(data)

    async def update_api_key(
        self,
        identifier: str,
        allowed_aliases: list[str],
    ) -> ApiKeyUpdateResponse:
        """Update API key permissions (admin only)."""
        data = await self._http.put(
            f"/api/v1/permissions/{identifier}",
            json=ApiKeyUpdateRequest(
                allowed_aliases=allowed_aliases
            ).model_dump(),
        )
        return ApiKeyUpdateResponse.model_validate(data)

    async def delete_api_key(self, identifier: str) -> DeleteResponse:
        """Revoke API key (admin only)."""
        data = await self._http.delete(f"/api/v1/permissions/{identifier}")
        return DeleteResponse.model_validate(data)

    # -------------------------------------------------------------------------
    # Monitoring
    # -------------------------------------------------------------------------

    async def health(self) -> HealthResponse:
        """Check service health."""
        data = await self._http.get("/health")
        return HealthResponse.model_validate(data)

    async def driver_pool_stats(self) -> DriverPoolStats:
        """Get driver pool stats (admin only)."""
        data = await self._http.get("/api/v1/driver-pool-stats")
        return DriverPoolStats.model_validate(data)

    # -------------------------------------------------------------------------
    # Convenience Methods - Graph Traversals
    # -------------------------------------------------------------------------

    async def get_clients(
        self, alias: str | None = None
    ) -> list[ClientNode]:
        """Get all Client nodes."""
        result = await self.cypher_query(
            "MATCH (c:Client) RETURN c", alias=alias
        )
        return [n for n in result.get_nodes() if isinstance(n, ClientNode)]

    async def get_applications(
        self,
        client_name: str | None = None,
        alias: str | None = None,
    ) -> list[ApplicationNode]:
        """Get Application nodes, optionally filtered by client."""
        if client_name:
            escaped = _escape_cypher_string(client_name)
            query = (
                f"MATCH (c:Client {{name: '{escaped}'}})"
                "-[:has_application]->(a:Application) RETURN a"
            )
        else:
            query = "MATCH (a:Application) RETURN a"
        result = await self.cypher_query(query, alias=alias)
        return [
            n for n in result.get_nodes() if isinstance(n, ApplicationNode)
        ]

    async def get_modules(
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
        result = await self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ModuleNode)]

    async def get_classes_in_module(
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
        result = await self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ClassNode)]

    async def get_methods_of_class(
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
        result = await self.cypher_query(query, alias=alias)
        nodes = result.get_nodes()
        return [n for n in nodes if isinstance(n, SubroutineNode)]

    async def get_attributes_of_class(
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
        result = await self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, AttributeNode)]

    async def get_class_hierarchy(
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
        result = await self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ClassNode)]

    async def get_subroutines_in_module(
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
        result = await self.cypher_query(query, alias=alias)
        nodes = result.get_nodes()
        return [n for n in nodes if isinstance(n, SubroutineNode)]

    async def get_module_imports(
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
        result = await self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ModuleNode)]

    async def get_callers_of_subroutine(
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
        result = await self.cypher_query(query, alias=alias)
        nodes = result.get_nodes()
        return [n for n in nodes if isinstance(n, SubroutineNode)]

    async def get_objects_used_by_subroutine(
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
        result = await self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ObjectNode)]

    async def get_instances_of_class(
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
        result = await self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ObjectNode)]

    async def get_subclasses(
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
        result = await self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ClassNode)]

    async def get_full_module_structure(
        self,
        module_name: str,
        alias: str | None = None,
    ) -> dict[str, Any]:
        """
        Get complete module structure with classes, functions, imports.

        Returns dict with keys: 'classes', 'subroutines', 'imports'.
        """
        classes = await self.get_classes_in_module(module_name, alias)
        subroutines = await self.get_subroutines_in_module(module_name, alias)
        imports = await self.get_module_imports(module_name, alias)
        return {
            "classes": classes,
            "subroutines": subroutines,
            "imports": imports,
        }

    async def get_full_class_structure(
        self,
        class_name: str,
        alias: str | None = None,
    ) -> dict[str, Any]:
        """
        Get complete class structure with methods, attributes, hierarchy.

        Returns dict with keys: 'methods', 'attributes', 'parents',
        'children', 'instances'.
        """
        methods = await self.get_methods_of_class(class_name, alias)
        attributes = await self.get_attributes_of_class(class_name, alias)
        parents = await self.get_class_hierarchy(class_name, alias)
        children = await self.get_subclasses(class_name, alias)
        instances = await self.get_instances_of_class(class_name, alias)
        return {
            "methods": methods,
            "attributes": attributes,
            "parents": parents,
            "children": children,
            "instances": instances,
        }
