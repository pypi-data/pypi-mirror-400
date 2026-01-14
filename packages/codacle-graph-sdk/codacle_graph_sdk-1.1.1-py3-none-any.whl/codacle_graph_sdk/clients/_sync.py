"""Synchronous Codacle Graph SDK client."""

from __future__ import annotations

from typing import Any

from .._core._http import HttpClient
from .._core._validation import detect_write_operation
from ..exceptions import ForbiddenError
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
    Neo4jCredentialsRequest,
    NodeData,
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
    Neo4jCredentialsResponse,
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
        read_only: If True (default), blocks write operations (CREATE, DELETE,
            MERGE, SET, REMOVE, etc.) client-side before sending to server.
            Set to False to enable write operations.

    Raises:
        AuthenticationError: If API key is missing, empty, or contains
            invalid characters (null bytes, non-latin1 unicode).

    Example:
        >>> # Read-only by default (safe)
        >>> client = Client(
        ...     url="https://api.codacle.com",
        ...     api_key="your-api-key",
        ...     alias="production-db",
        ... )
        >>> result = client.cypher_query("MATCH (c:Class) RETURN c")
        >>> for node in result.get_nodes():
        ...     print(node.name)

        >>> # Enable writes explicitly
        >>> client = Client(api_key="your-key", read_only=False)
        >>> client.cypher_query("CREATE (n:Test) RETURN n")
    """

    def __init__(
        self,
        url: str,
        api_key: str,
        alias: str | None = None,
        timeout: float = 30.0,
        read_only: bool = True,
    ):
        self._http = HttpClient(url, api_key, timeout)
        self._default_alias = alias
        self._read_only = read_only

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

        Raises:
            ForbiddenError: If read_only=True and query contains write ops.
            ValidationError: If query is empty or contains invalid characters.
            Neo4jQueryError: If query execution fails.
        """
        # Check read-only mode (enabled by default)
        if self._read_only and detect_write_operation(query):
            raise ForbiddenError(
                "Write operations are not allowed in read-only mode. "
                f"Detected write operation in query: {query[:50]}... "
                "Set read_only=False to enable write operations.",
                status_code=403,
            )

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

    # -------------------------------------------------------------------------
    # Convenience Methods - Class Operations
    # -------------------------------------------------------------------------

    def get_all_classes(
        self,
        limit: int | None = None,
        alias: str | None = None,
    ) -> list[ClassNode]:
        """
        Get all Class nodes in the graph.

        Args:
            limit: Maximum number of results (None for unlimited).
            alias: Neo4j instance alias.

        Returns:
            List of ClassNode instances.

        Example:
            >>> classes = client.get_all_classes(limit=100)
            >>> for cls in classes:
            ...     print(f"{cls.name}: abstract={cls.is_abstract}")
        """
        limit_clause = f" LIMIT {limit}" if limit else ""
        query = f"MATCH (c:Class) RETURN c{limit_clause}"
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ClassNode)]

    def find_class_by_name(
        self,
        name: str,
        alias: str | None = None,
    ) -> ClassNode | None:
        """
        Find a class by exact name match.

        Args:
            name: Exact class name to find.
            alias: Neo4j instance alias.

        Returns:
            ClassNode if found, None otherwise.

        Example:
            >>> cls = client.find_class_by_name("UserService")
            >>> if cls:
            ...     print(cls.docstring)
        """
        escaped = _escape_cypher_string(name)
        query = f"MATCH (c:Class {{name: '{escaped}'}}) RETURN c LIMIT 1"
        result = self.cypher_query(query, alias=alias)
        nodes = [n for n in result.get_nodes() if isinstance(n, ClassNode)]
        return nodes[0] if nodes else None

    def find_classes_by_name_pattern(
        self,
        pattern: str,
        alias: str | None = None,
    ) -> list[ClassNode]:
        """
        Find classes matching a regex pattern on name.

        Args:
            pattern: Regex pattern (Neo4j =~ operator syntax).
            alias: Neo4j instance alias.

        Returns:
            List of matching ClassNode instances.

        Example:
            >>> # Find all classes ending with "Service"
            >>> services = client.find_classes_by_name_pattern(".*Service$")
            >>> # Find all classes starting with "User"
            >>> user_classes = client.find_classes_by_name_pattern("^User.*")
        """
        escaped = _escape_cypher_string(pattern)
        query = f"MATCH (c:Class) WHERE c.name =~ '{escaped}' RETURN c"
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ClassNode)]

    def find_classes_by_metadata(
        self,
        filters: dict[str, Any],
        alias: str | None = None,
    ) -> list[ClassNode]:
        """
        Find classes matching metadata field filters.

        Args:
            filters: Dictionary of field-value pairs to match.
            alias: Neo4j instance alias.

        Returns:
            List of ClassNode instances matching all filters.

        Example:
            >>> # Find abstract classes
            >>> abstract = client.find_classes_by_metadata({"is_abstract": True})  # noqa: E501
            >>> # Find classes by custom field
            >>> tagged = client.find_classes_by_metadata({"deprecated": True})
        """
        if not filters:
            return self.get_all_classes(alias=alias)

        conditions = []
        for key, value in filters.items():
            escaped_key = _escape_cypher_string(key)
            if isinstance(value, str):
                escaped_val = _escape_cypher_string(value)
                conditions.append(f"c.`{escaped_key}` = '{escaped_val}'")
            elif isinstance(value, bool):
                conditions.append(f"c.`{escaped_key}` = {str(value).lower()}")
            elif isinstance(value, int | float):
                conditions.append(f"c.`{escaped_key}` = {value}")
            else:
                escaped_val = _escape_cypher_string(str(value))
                conditions.append(f"c.`{escaped_key}` = '{escaped_val}'")

        where_clause = " AND ".join(conditions)
        query = f"MATCH (c:Class) WHERE {where_clause} RETURN c"
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ClassNode)]

    def count_classes(self, alias: str | None = None) -> int:
        """
        Count total number of Class nodes.

        Args:
            alias: Neo4j instance alias.

        Returns:
            Number of Class nodes in the graph.

        Example:
            >>> total = client.count_classes()
            >>> print(f"Total classes: {total}")
        """
        query = "MATCH (c:Class) RETURN count(c) AS count"
        result = self.cypher_query(query, alias=alias)
        if result.results and "count" in result.results[0]:
            return int(result.results[0]["count"])
        return 0

    def class_exists(self, name: str, alias: str | None = None) -> bool:
        """
        Check if a class with the given name exists.

        Args:
            name: Class name to check.
            alias: Neo4j instance alias.

        Returns:
            True if class exists, False otherwise.

        Example:
            >>> if client.class_exists("UserService"):
            ...     print("Class found")
        """
        escaped = _escape_cypher_string(name)
        query = (
            f"MATCH (c:Class {{name: '{escaped}'}}) "
            "RETURN count(c) > 0 AS exists"
        )
        result = self.cypher_query(query, alias=alias)
        if result.results and "exists" in result.results[0]:
            return bool(result.results[0]["exists"])
        return False

    # -------------------------------------------------------------------------
    # Convenience Methods - Module Operations
    # -------------------------------------------------------------------------

    def get_all_modules(
        self,
        limit: int | None = None,
        alias: str | None = None,
    ) -> list[ModuleNode]:
        """
        Get all Module nodes in the graph.

        Args:
            limit: Maximum number of results.
            alias: Neo4j instance alias.

        Returns:
            List of ModuleNode instances.

        Example:
            >>> modules = client.get_all_modules(limit=50)
        """
        limit_clause = f" LIMIT {limit}" if limit else ""
        query = f"MATCH (m:Module) RETURN m{limit_clause}"
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ModuleNode)]

    def find_module_by_name(
        self,
        name: str,
        alias: str | None = None,
    ) -> ModuleNode | None:
        """
        Find a module by exact name match.

        Args:
            name: Exact module name to find.
            alias: Neo4j instance alias.

        Returns:
            ModuleNode if found, None otherwise.

        Example:
            >>> mod = client.find_module_by_name("utils")
        """
        escaped = _escape_cypher_string(name)
        query = f"MATCH (m:Module {{name: '{escaped}'}}) RETURN m LIMIT 1"
        result = self.cypher_query(query, alias=alias)
        nodes = [n for n in result.get_nodes() if isinstance(n, ModuleNode)]
        return nodes[0] if nodes else None

    def find_modules_by_name_pattern(
        self,
        pattern: str,
        alias: str | None = None,
    ) -> list[ModuleNode]:
        """
        Find modules matching a regex pattern on name.

        Args:
            pattern: Regex pattern (Neo4j =~ operator syntax).
            alias: Neo4j instance alias.

        Returns:
            List of matching ModuleNode instances.

        Example:
            >>> # Find all test modules
            >>> test_modules = client.find_modules_by_name_pattern("^test_.*")
        """
        escaped = _escape_cypher_string(pattern)
        query = f"MATCH (m:Module) WHERE m.name =~ '{escaped}' RETURN m"
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ModuleNode)]

    def find_modules_by_path_pattern(
        self,
        pattern: str,
        alias: str | None = None,
    ) -> list[ModuleNode]:
        """
        Find modules matching a regex pattern on path.

        Args:
            pattern: Regex pattern for path matching.
            alias: Neo4j instance alias.

        Returns:
            List of matching ModuleNode instances.

        Example:
            >>> # Find all modules in src/services directory
            >>> svc = client.find_modules_by_path_pattern(".*src/services/.*")
        """
        escaped = _escape_cypher_string(pattern)
        query = f"MATCH (m:Module) WHERE m.path =~ '{escaped}' RETURN m"
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ModuleNode)]

    def find_modules_by_metadata(
        self,
        filters: dict[str, Any],
        alias: str | None = None,
    ) -> list[ModuleNode]:
        """
        Find modules matching metadata field filters.

        Args:
            filters: Dictionary of field-value pairs to match.
            alias: Neo4j instance alias.

        Returns:
            List of ModuleNode instances matching all filters.
        """
        if not filters:
            return self.get_all_modules(alias=alias)

        conditions = []
        for key, value in filters.items():
            escaped_key = _escape_cypher_string(key)
            if isinstance(value, str):
                escaped_val = _escape_cypher_string(value)
                conditions.append(f"m.`{escaped_key}` = '{escaped_val}'")
            elif isinstance(value, bool):
                conditions.append(f"m.`{escaped_key}` = {str(value).lower()}")
            elif isinstance(value, int | float):
                conditions.append(f"m.`{escaped_key}` = {value}")
            else:
                escaped_val = _escape_cypher_string(str(value))
                conditions.append(f"m.`{escaped_key}` = '{escaped_val}'")

        where_clause = " AND ".join(conditions)
        query = f"MATCH (m:Module) WHERE {where_clause} RETURN m"
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ModuleNode)]

    def count_modules(self, alias: str | None = None) -> int:
        """
        Count total number of Module nodes.

        Args:
            alias: Neo4j instance alias.

        Returns:
            Number of Module nodes in the graph.
        """
        query = "MATCH (m:Module) RETURN count(m) AS count"
        result = self.cypher_query(query, alias=alias)
        if result.results and "count" in result.results[0]:
            return int(result.results[0]["count"])
        return 0

    def module_exists(self, name: str, alias: str | None = None) -> bool:
        """
        Check if a module with the given name exists.

        Args:
            name: Module name to check.
            alias: Neo4j instance alias.

        Returns:
            True if module exists, False otherwise.
        """
        escaped = _escape_cypher_string(name)
        query = (
            f"MATCH (m:Module {{name: '{escaped}'}}) "
            "RETURN count(m) > 0 AS exists"
        )
        result = self.cypher_query(query, alias=alias)
        if result.results and "exists" in result.results[0]:
            return bool(result.results[0]["exists"])
        return False

    # -------------------------------------------------------------------------
    # Convenience Methods - Subroutine Operations
    # -------------------------------------------------------------------------

    def get_all_subroutines(
        self,
        limit: int | None = None,
        alias: str | None = None,
    ) -> list[SubroutineNode]:
        """
        Get all Subroutine nodes in the graph.

        Args:
            limit: Maximum number of results.
            alias: Neo4j instance alias.

        Returns:
            List of SubroutineNode instances.
        """
        limit_clause = f" LIMIT {limit}" if limit else ""
        query = f"MATCH (s:Subroutine) RETURN s{limit_clause}"
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, SubroutineNode)]

    def find_subroutine_by_name(
        self,
        name: str,
        alias: str | None = None,
    ) -> SubroutineNode | None:
        """
        Find a subroutine by exact name match.

        Args:
            name: Exact subroutine name to find.
            alias: Neo4j instance alias.

        Returns:
            SubroutineNode if found, None otherwise.
        """
        escaped = _escape_cypher_string(name)
        query = f"MATCH (s:Subroutine {{name: '{escaped}'}}) RETURN s LIMIT 1"
        result = self.cypher_query(query, alias=alias)
        nodes = [
            n for n in result.get_nodes() if isinstance(n, SubroutineNode)
        ]
        return nodes[0] if nodes else None

    def find_subroutines_by_name_pattern(
        self,
        pattern: str,
        alias: str | None = None,
    ) -> list[SubroutineNode]:
        """
        Find subroutines matching a regex pattern on name.

        Args:
            pattern: Regex pattern (Neo4j =~ operator syntax).
            alias: Neo4j instance alias.

        Returns:
            List of matching SubroutineNode instances.

        Example:
            >>> # Find all getter methods
            >>> getters = client.find_subroutines_by_name_pattern("^get_.*")
            >>> # Find all private methods
            >>> private = client.find_subroutines_by_name_pattern("^_[^_].*")
        """
        escaped = _escape_cypher_string(pattern)
        query = f"MATCH (s:Subroutine) WHERE s.name =~ '{escaped}' RETURN s"
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, SubroutineNode)]

    def find_subroutines_by_return_type(
        self,
        return_type: str,
        alias: str | None = None,
    ) -> list[SubroutineNode]:
        """
        Find subroutines with a specific return type.

        Args:
            return_type: Return type annotation to match.
            alias: Neo4j instance alias.

        Returns:
            List of SubroutineNode instances with matching return type.

        Example:
            >>> # Find all functions returning bool
            >>> bool_funcs = client.find_subroutines_by_return_type("bool")
        """
        escaped = _escape_cypher_string(return_type)
        query = f"MATCH (s:Subroutine {{return_type: '{escaped}'}}) RETURN s"
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, SubroutineNode)]

    def find_subroutines_by_metadata(
        self,
        filters: dict[str, Any],
        alias: str | None = None,
    ) -> list[SubroutineNode]:
        """
        Find subroutines matching metadata field filters.

        Args:
            filters: Dictionary of field-value pairs to match.
            alias: Neo4j instance alias.

        Returns:
            List of SubroutineNode instances matching all filters.
        """
        if not filters:
            return self.get_all_subroutines(alias=alias)

        conditions = []
        for key, value in filters.items():
            escaped_key = _escape_cypher_string(key)
            if isinstance(value, str):
                escaped_val = _escape_cypher_string(value)
                conditions.append(f"s.`{escaped_key}` = '{escaped_val}'")
            elif isinstance(value, bool):
                conditions.append(f"s.`{escaped_key}` = {str(value).lower()}")
            elif isinstance(value, int | float):
                conditions.append(f"s.`{escaped_key}` = {value}")
            else:
                escaped_val = _escape_cypher_string(str(value))
                conditions.append(f"s.`{escaped_key}` = '{escaped_val}'")

        where_clause = " AND ".join(conditions)
        query = f"MATCH (s:Subroutine) WHERE {where_clause} RETURN s"
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, SubroutineNode)]

    def count_subroutines(self, alias: str | None = None) -> int:
        """
        Count total number of Subroutine nodes.

        Args:
            alias: Neo4j instance alias.

        Returns:
            Number of Subroutine nodes in the graph.
        """
        query = "MATCH (s:Subroutine) RETURN count(s) AS count"
        result = self.cypher_query(query, alias=alias)
        if result.results and "count" in result.results[0]:
            return int(result.results[0]["count"])
        return 0

    def subroutine_exists(self, name: str, alias: str | None = None) -> bool:
        """
        Check if a subroutine with the given name exists.

        Args:
            name: Subroutine name to check.
            alias: Neo4j instance alias.

        Returns:
            True if subroutine exists, False otherwise.
        """
        escaped = _escape_cypher_string(name)
        query = (
            f"MATCH (s:Subroutine {{name: '{escaped}'}}) "
            "RETURN count(s) > 0 AS exists"
        )
        result = self.cypher_query(query, alias=alias)
        if result.results and "exists" in result.results[0]:
            return bool(result.results[0]["exists"])
        return False

    # -------------------------------------------------------------------------
    # Convenience Methods - Attribute Operations
    # -------------------------------------------------------------------------

    def get_all_attributes(
        self,
        limit: int | None = None,
        alias: str | None = None,
    ) -> list[AttributeNode]:
        """
        Get all Attribute nodes in the graph.

        Args:
            limit: Maximum number of results.
            alias: Neo4j instance alias.

        Returns:
            List of AttributeNode instances.
        """
        limit_clause = f" LIMIT {limit}" if limit else ""
        query = f"MATCH (a:Attribute) RETURN a{limit_clause}"
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, AttributeNode)]

    def find_attribute_by_name(
        self,
        name: str,
        alias: str | None = None,
    ) -> AttributeNode | None:
        """
        Find an attribute by exact name match.

        Args:
            name: Exact attribute name to find.
            alias: Neo4j instance alias.

        Returns:
            AttributeNode if found, None otherwise.
        """
        escaped = _escape_cypher_string(name)
        query = f"MATCH (a:Attribute {{name: '{escaped}'}}) RETURN a LIMIT 1"
        result = self.cypher_query(query, alias=alias)
        nodes = [n for n in result.get_nodes() if isinstance(n, AttributeNode)]
        return nodes[0] if nodes else None

    def find_attributes_by_name_pattern(
        self,
        pattern: str,
        alias: str | None = None,
    ) -> list[AttributeNode]:
        """
        Find attributes matching a regex pattern on name.

        Args:
            pattern: Regex pattern (Neo4j =~ operator syntax).
            alias: Neo4j instance alias.

        Returns:
            List of matching AttributeNode instances.

        Example:
            >>> # Find all private attributes
            >>> private = client.find_attributes_by_name_pattern("^_.*")
        """
        escaped = _escape_cypher_string(pattern)
        query = f"MATCH (a:Attribute) WHERE a.name =~ '{escaped}' RETURN a"
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, AttributeNode)]

    def find_attributes_by_type(
        self,
        type_annotation: str,
        alias: str | None = None,
    ) -> list[AttributeNode]:
        """
        Find attributes with a specific type annotation.

        Args:
            type_annotation: Type annotation to match (e.g., "str", "int").
            alias: Neo4j instance alias.

        Returns:
            List of AttributeNode instances with matching type.

        Example:
            >>> # Find all string attributes
            >>> str_attrs = client.find_attributes_by_type("str")
        """
        escaped = _escape_cypher_string(type_annotation)
        query = (
            f"MATCH (a:Attribute {{type_annotation: '{escaped}'}}) RETURN a"
        )
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, AttributeNode)]

    def count_attributes(self, alias: str | None = None) -> int:
        """
        Count total number of Attribute nodes.

        Args:
            alias: Neo4j instance alias.

        Returns:
            Number of Attribute nodes in the graph.
        """
        query = "MATCH (a:Attribute) RETURN count(a) AS count"
        result = self.cypher_query(query, alias=alias)
        if result.results and "count" in result.results[0]:
            return int(result.results[0]["count"])
        return 0

    def attribute_exists(self, name: str, alias: str | None = None) -> bool:
        """
        Check if an attribute with the given name exists.

        Args:
            name: Attribute name to check.
            alias: Neo4j instance alias.

        Returns:
            True if attribute exists, False otherwise.
        """
        escaped = _escape_cypher_string(name)
        query = (
            f"MATCH (a:Attribute {{name: '{escaped}'}}) "
            "RETURN count(a) > 0 AS exists"
        )
        result = self.cypher_query(query, alias=alias)
        if result.results and "exists" in result.results[0]:
            return bool(result.results[0]["exists"])
        return False

    # -------------------------------------------------------------------------
    # Convenience Methods - Relationship Traversals
    # -------------------------------------------------------------------------

    def get_classes_inheriting_from(
        self,
        base_class_name: str,
        recursive: bool = False,
        alias: str | None = None,
    ) -> list[ClassNode]:
        """
        Get all classes that inherit from a given base class.

        Args:
            base_class_name: Name of the base class.
            recursive: If True, get all descendants (transitive closure).
            alias: Neo4j instance alias.

        Returns:
            List of ClassNode instances that inherit from the base.

        Example:
            >>> # Find direct subclasses only
            >>> direct = client.get_classes_inheriting_from("BaseModel")
            >>> # Find all descendants
            >>> all_sub = client.get_classes_inheriting_from("BaseModel", True)
        """
        escaped = _escape_cypher_string(base_class_name)
        depth = "*1.." if recursive else ""
        query = (
            f"MATCH (child:Class)-[:inherits_from{depth}]->"
            f"(base:Class {{name: '{escaped}'}}) RETURN DISTINCT child"
        )
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ClassNode)]

    def get_base_classes(
        self,
        class_name: str,
        recursive: bool = False,
        alias: str | None = None,
    ) -> list[ClassNode]:
        """
        Get base classes of a given class.

        Args:
            class_name: Name of the derived class.
            recursive: If True, get all ancestors (transitive closure).
            alias: Neo4j instance alias.

        Returns:
            List of ClassNode instances that are bases of the given class.

        Example:
            >>> # Get direct parents only
            >>> parents = client.get_base_classes("UserService")
            >>> # Get all ancestors
            >>> ancestors = client.get_base_classes("UserService", True)
        """
        escaped = _escape_cypher_string(class_name)
        depth = "*1.." if recursive else ""
        query = (
            f"MATCH (c:Class {{name: '{escaped}'}})"
            f"-[:inherits_from{depth}]->(base:Class) RETURN DISTINCT base"
        )
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ClassNode)]

    def get_subroutines_calling(
        self,
        subroutine_name: str,
        alias: str | None = None,
    ) -> list[SubroutineNode]:
        """
        Get all subroutines that call/trigger the given subroutine.

        Args:
            subroutine_name: Name of the target subroutine.
            alias: Neo4j instance alias.

        Returns:
            List of SubroutineNode instances that call the target.

        Example:
            >>> callers = client.get_subroutines_calling("validate_user")
        """
        escaped = _escape_cypher_string(subroutine_name)
        query = (
            f"MATCH (caller:Subroutine)-[:triggers]->"
            f"(s:Subroutine {{name: '{escaped}'}}) RETURN caller"
        )
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, SubroutineNode)]

    def get_subroutines_called_by(
        self,
        subroutine_name: str,
        alias: str | None = None,
    ) -> list[SubroutineNode]:
        """
        Get all subroutines that are called/triggered by the given subroutine.

        Args:
            subroutine_name: Name of the caller subroutine.
            alias: Neo4j instance alias.

        Returns:
            List of SubroutineNode instances called by the source.

        Example:
            >>> callees = client.get_subroutines_called_by("process_request")
        """
        escaped = _escape_cypher_string(subroutine_name)
        query = (
            f"MATCH (s:Subroutine {{name: '{escaped}'}})"
            "-[:triggers]->(callee:Subroutine) RETURN callee"
        )
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, SubroutineNode)]

    def get_modules_importing(
        self,
        module_name: str,
        alias: str | None = None,
    ) -> list[ModuleNode]:
        """
        Get all modules that import the given module (dependents).

        Args:
            module_name: Name of the imported module.
            alias: Neo4j instance alias.

        Returns:
            List of ModuleNode instances that import the target.

        Example:
            >>> # Find who depends on utils module
            >>> dependents = client.get_modules_importing("utils")
        """
        escaped = _escape_cypher_string(module_name)
        query = (
            f"MATCH (importer:Module)-[:contains_imports]->"
            f"(m:Module {{name: '{escaped}'}}) RETURN importer"
        )
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ModuleNode)]

    def get_modules_imported_by(
        self,
        module_name: str,
        alias: str | None = None,
    ) -> list[ModuleNode]:
        """
        Get all modules that are imported by the given module (dependencies).

        Args:
            module_name: Name of the importing module.
            alias: Neo4j instance alias.

        Returns:
            List of ModuleNode instances that are dependencies.

        Example:
            >>> # Find dependencies of user_service module
            >>> deps = client.get_modules_imported_by("user_service")
        """
        escaped = _escape_cypher_string(module_name)
        query = (
            f"MATCH (m:Module {{name: '{escaped}'}})"
            "-[:contains_imports]->(imported:Module) RETURN imported"
        )
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ModuleNode)]

    def get_classes_used_by_subroutine(
        self,
        subroutine_name: str,
        alias: str | None = None,
    ) -> list[ClassNode]:
        """
        Get all classes instantiated or used by a subroutine.

        Args:
            subroutine_name: Name of the subroutine.
            alias: Neo4j instance alias.

        Returns:
            List of ClassNode instances used by the subroutine.

        Example:
            >>> classes = client.get_classes_used_by_subroutine("create_user")
        """
        escaped = _escape_cypher_string(subroutine_name)
        query = (
            f"MATCH (s:Subroutine {{name: '{escaped}'}})"
            "-[:instantiates_class]->(c:Class) RETURN c"
        )
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ClassNode)]

    def get_subroutines_using_class(
        self,
        class_name: str,
        alias: str | None = None,
    ) -> list[SubroutineNode]:
        """
        Get all subroutines that instantiate or use a given class.

        Args:
            class_name: Name of the class.
            alias: Neo4j instance alias.

        Returns:
            List of SubroutineNode instances that use the class.

        Example:
            >>> users = client.get_subroutines_using_class("DatabaseConnection")  # noqa: E501
        """
        escaped = _escape_cypher_string(class_name)
        query = (
            f"MATCH (s:Subroutine)-[:instantiates_class]->"
            f"(c:Class {{name: '{escaped}'}}) RETURN s"
        )
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, SubroutineNode)]

    # -------------------------------------------------------------------------
    # Convenience Methods - Advanced Queries
    # -------------------------------------------------------------------------

    def find_async_subroutines(
        self,
        alias: str | None = None,
    ) -> list[SubroutineNode]:
        """
        Find all asynchronous subroutines (async def).

        Args:
            alias: Neo4j instance alias.

        Returns:
            List of async SubroutineNode instances.

        Example:
            >>> async_funcs = client.find_async_subroutines()
            >>> for func in async_funcs:
            ...     print(f"async {func.name}")
        """
        query = "MATCH (s:Subroutine {is_async: true}) RETURN s"
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, SubroutineNode)]

    def find_abstract_classes(
        self,
        alias: str | None = None,
    ) -> list[ClassNode]:
        """
        Find all abstract classes.

        Args:
            alias: Neo4j instance alias.

        Returns:
            List of abstract ClassNode instances.

        Example:
            >>> abstract = client.find_abstract_classes()
            >>> for cls in abstract:
            ...     print(f"ABC: {cls.name}")
        """
        query = "MATCH (c:Class {is_abstract: true}) RETURN c"
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ClassNode)]

    def find_classes_with_base(
        self,
        base_name: str,
        alias: str | None = None,
    ) -> list[ClassNode]:
        """
        Find classes that have a specific base in their bases list.

        Note: This checks the 'bases' property array, not the relationship.
        Use get_classes_inheriting_from() for relationship-based traversal.

        Args:
            base_name: Base class name to search for in bases array.
            alias: Neo4j instance alias.

        Returns:
            List of ClassNode instances with the base in their bases list.

        Example:
            >>> models = client.find_classes_with_base("BaseModel")
        """
        escaped = _escape_cypher_string(base_name)
        query = f"MATCH (c:Class) WHERE '{escaped}' IN c.bases RETURN c"
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ClassNode)]

    def find_orphan_classes(
        self,
        alias: str | None = None,
    ) -> list[ClassNode]:
        """
        Find classes not contained by any module.

        Args:
            alias: Neo4j instance alias.

        Returns:
            List of ClassNode instances with no parent module.

        Example:
            >>> orphans = client.find_orphan_classes()
            >>> print(f"Found {len(orphans)} orphan classes")
        """
        query = (
            "MATCH (c:Class) "
            "WHERE NOT ((:Module)-[:has_class]->(c)) "
            "RETURN c"
        )
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ClassNode)]

    def find_orphan_subroutines(
        self,
        alias: str | None = None,
    ) -> list[SubroutineNode]:
        """
        Find subroutines not defined in any module or class.

        Args:
            alias: Neo4j instance alias.

        Returns:
            List of orphan SubroutineNode instances.
        """
        query = (
            "MATCH (s:Subroutine) "
            "WHERE NOT (()-[:has_subroutine|defines_method]->(s)) "
            "RETURN s"
        )
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, SubroutineNode)]

    def get_classes_with_method_count(
        self,
        min_methods: int = 0,
        max_methods: int | None = None,
        alias: str | None = None,
    ) -> list[tuple[ClassNode, int]]:
        """
        Get classes with their method count, filtered by range.

        Args:
            min_methods: Minimum method count (inclusive).
            max_methods: Maximum method count (inclusive), None for unlimited.
            alias: Neo4j instance alias.

        Returns:
            List of (ClassNode, method_count) tuples.

        Example:
            >>> # Find large classes (potential code smell)
            >>> large = client.get_classes_with_method_count(min_methods=20)
            >>> for cls, count in large:
            ...     print(f"{cls.name}: {count} methods")
        """
        from ..models.nodes import parse_node

        max_clause = f" AND cnt <= {max_methods}" if max_methods else ""
        query = (
            "MATCH (c:Class) "
            "OPTIONAL MATCH (c)-[:defines_method]->(m:Subroutine) "
            f"WITH c, count(m) AS cnt WHERE cnt >= {min_methods}{max_clause} "
            "RETURN c, cnt ORDER BY cnt DESC"
        )
        result = self.cypher_query(query, alias=alias)
        output: list[tuple[ClassNode, int]] = []
        for row in result.results:
            if "c" in row and "cnt" in row:
                node = parse_node(row["c"])
                if isinstance(node, ClassNode):
                    output.append((node, row["cnt"]))
        return output

    # -------------------------------------------------------------------------
    # Convenience Methods - Batch Operations
    # -------------------------------------------------------------------------

    def get_classes_by_names(
        self,
        names: list[str],
        alias: str | None = None,
    ) -> list[ClassNode]:
        """
        Get multiple classes by their names in a single query.

        Args:
            names: List of class names to retrieve.
            alias: Neo4j instance alias.

        Returns:
            List of ClassNode instances found (may be fewer than requested).

        Example:
            >>> classes = client.get_classes_by_names(
            ...     ["UserService", "OrderService"]
            ... )
        """
        if not names:
            return []
        escaped_names = [f"'{_escape_cypher_string(n)}'" for n in names]
        names_list = ", ".join(escaped_names)
        query = f"MATCH (c:Class) WHERE c.name IN [{names_list}] RETURN c"
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ClassNode)]

    def get_modules_by_names(
        self,
        names: list[str],
        alias: str | None = None,
    ) -> list[ModuleNode]:
        """
        Get multiple modules by their names in a single query.

        Args:
            names: List of module names to retrieve.
            alias: Neo4j instance alias.

        Returns:
            List of ModuleNode instances found.
        """
        if not names:
            return []
        escaped_names = [f"'{_escape_cypher_string(n)}'" for n in names]
        names_list = ", ".join(escaped_names)
        query = f"MATCH (m:Module) WHERE m.name IN [{names_list}] RETURN m"
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, ModuleNode)]

    def get_subroutines_by_names(
        self,
        names: list[str],
        alias: str | None = None,
    ) -> list[SubroutineNode]:
        """
        Get multiple subroutines by their names in a single query.

        Args:
            names: List of subroutine names to retrieve.
            alias: Neo4j instance alias.

        Returns:
            List of SubroutineNode instances found.
        """
        if not names:
            return []
        escaped_names = [f"'{_escape_cypher_string(n)}'" for n in names]
        names_list = ", ".join(escaped_names)
        query = f"MATCH (s:Subroutine) WHERE s.name IN [{names_list}] RETURN s"
        result = self.cypher_query(query, alias=alias)
        return [n for n in result.get_nodes() if isinstance(n, SubroutineNode)]
