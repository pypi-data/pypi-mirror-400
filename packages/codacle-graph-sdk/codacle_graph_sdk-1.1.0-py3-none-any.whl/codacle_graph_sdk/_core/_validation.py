"""Input validation utilities for the SDK."""

from __future__ import annotations

import re

# Forbidden Cypher keywords for read-only clients
WRITE_KEYWORDS = frozenset({
    "CREATE",
    "MERGE",
    "DELETE",
    "DETACH",
    "SET",
    "REMOVE",
    "DROP",
    "ALTER",
    "GRANT",
    "DENY",
    "REVOKE",
})

# Pattern to detect null bytes and other dangerous control characters
# Excludes tab (\x09), newline (\x0a), carriage return (\x0d)
DANGEROUS_CHARS_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

# Valid alias pattern: alphanumeric start, then alphanumeric/dots/hyphens
ALIAS_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9.\-]*$")


def validate_api_key(api_key: str) -> str:
    """Validate API key for HTTP header compatibility.

    Args:
        api_key: The API key to validate.

    Returns:
        The validated API key.

    Raises:
        ValueError: If API key is empty, contains null bytes, or has
            characters that cannot be encoded as HTTP headers (latin-1).
    """
    if not api_key:
        raise ValueError("API key cannot be empty")

    # Check for null bytes
    if "\x00" in api_key:
        raise ValueError("API key cannot contain null bytes")

    # HTTP headers must be encodable as latin-1
    try:
        api_key.encode("latin-1")
    except UnicodeEncodeError as e:
        raise ValueError(
            f"API key contains invalid characters for HTTP headers: {e.reason}"
        ) from e

    return api_key


def validate_query_string(query: str, *, allow_empty: bool = False) -> str:
    """Validate query string for dangerous content.

    Args:
        query: The query string to validate.
        allow_empty: If True, allows empty/whitespace-only queries.

    Returns:
        The validated query string.

    Raises:
        ValueError: If query is empty (when not allowed) or contains
            dangerous control characters.
    """
    if not allow_empty and not query.strip():
        raise ValueError("Query cannot be empty or whitespace-only")

    # Check for null bytes and dangerous control characters
    if DANGEROUS_CHARS_PATTERN.search(query):
        raise ValueError("Query contains invalid control characters")

    return query


def detect_write_operation(cypher_query: str) -> bool:
    """Detect if a Cypher query contains write operations.

    This function checks for Cypher keywords that modify data:
    CREATE, MERGE, DELETE, DETACH, SET, REMOVE, DROP, ALTER,
    GRANT, DENY, REVOKE.

    Args:
        cypher_query: The Cypher query to check.

    Returns:
        True if the query appears to modify data, False otherwise.
    """
    # Normalize: uppercase, remove string literals to avoid false positives
    normalized = _remove_string_literals(cypher_query.upper())

    # Check for write keywords at word boundaries
    for keyword in WRITE_KEYWORDS:
        pattern = rf"\b{keyword}\b"
        if re.search(pattern, normalized):
            return True

    return False


def _remove_string_literals(query: str) -> str:
    """Remove string literals to avoid false positives in keyword detection.

    Args:
        query: The query string (should be uppercase).

    Returns:
        Query with string literals replaced by empty strings.
    """
    # Remove single-quoted strings (handles escaped quotes)
    query = re.sub(r"'(?:[^'\\]|\\.)*'", "''", query)
    # Remove double-quoted strings (handles escaped quotes)
    query = re.sub(r'"(?:[^"\\]|\\.)*"', '""', query)
    return query


def validate_alias(alias: str | None) -> str | None:
    """Validate Neo4j alias format.

    Args:
        alias: The alias to validate, or None.

    Returns:
        The validated alias, or None if input was None.

    Raises:
        ValueError: If alias is empty, has invalid format, or contains
            path traversal attempts.
    """
    if alias is None:
        return None

    if not alias:
        raise ValueError("Alias cannot be empty string")

    if not ALIAS_PATTERN.match(alias):
        raise ValueError(
            f"Invalid alias format: '{alias}'. "
            "Alias must start with alphanumeric and contain only "
            "alphanumeric characters, dots, and hyphens."
        )

    # Check for path traversal attempts
    if ".." in alias or alias.startswith("."):
        raise ValueError("Invalid alias: path traversal not allowed")

    return alias
