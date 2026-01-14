"""API key response DTOs."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from ._utils import parse_mongo_date, parse_mongo_oid


class ApiKeyInfo(BaseModel):
    """API key info."""

    model_config = {"populate_by_name": True}

    id: str = Field(..., alias="_id")
    name: str
    api_key: str  # Full key on create, masked on list
    allowed_aliases: list[str]
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @field_validator("id", mode="before")
    @classmethod
    def parse_id(cls, v: Any) -> str:
        result = parse_mongo_oid(v)
        return result or ""

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def parse_dates(cls, v: Any) -> datetime | None:
        return parse_mongo_date(v)


class ApiKeyCreateResponse(BaseModel):
    """API key creation response."""

    message: str
    details: ApiKeyInfo


class ApiKeyListResponse(BaseModel):
    """List of API keys."""

    api_keys: list[ApiKeyInfo]


class ApiKeyUpdateResponse(BaseModel):
    """API key update response."""

    message: str
    details: dict[str, Any]
