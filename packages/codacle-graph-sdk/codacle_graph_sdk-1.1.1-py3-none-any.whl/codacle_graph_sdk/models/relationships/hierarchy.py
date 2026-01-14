"""Hierarchy relationship models."""

from __future__ import annotations

from typing import Literal

from .._base import BaseRelationship


class HasApplication(BaseRelationship):
    """Client has_application Application."""

    type: Literal["has_application"] = "has_application"


class HasModule(BaseRelationship):
    """Application has_module Module."""

    type: Literal["has_module"] = "has_module"


class HasSubroutine(BaseRelationship):
    """Module has_subroutine Subroutine."""

    type: Literal["has_subroutine"] = "has_subroutine"


class HasClass(BaseRelationship):
    """Module has_class Class."""

    type: Literal["has_class"] = "has_class"
