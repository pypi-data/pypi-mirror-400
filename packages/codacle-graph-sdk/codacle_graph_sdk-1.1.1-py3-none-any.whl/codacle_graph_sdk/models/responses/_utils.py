"""Response parsing utilities."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def parse_mongo_oid(value: Any) -> str | None:
    """Parse MongoDB ObjectId extended JSON format."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and "$oid" in value:
        oid: str = value["$oid"]
        return oid
    return str(value) if value else None


def parse_mongo_date(value: Any) -> datetime | None:
    """Parse MongoDB Date extended JSON format."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, dict) and "$date" in value:
        date_str = value["$date"]
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    return None
