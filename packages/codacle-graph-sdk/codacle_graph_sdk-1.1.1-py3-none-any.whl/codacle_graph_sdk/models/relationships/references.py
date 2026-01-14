"""Reference relationship models."""

from __future__ import annotations

from typing import Literal

from .._base import BaseRelationship


class HasMethod(BaseRelationship):
    """Object has_method Subroutine."""

    type: Literal["has_method"] = "has_method"


class Contains(BaseRelationship):
    """Object contains Object."""

    type: Literal["contains"] = "contains"


class Uses(BaseRelationship):
    """Subroutine uses Object."""

    type: Literal["uses"] = "uses"


class Refers(BaseRelationship):
    """Attribute refers Class or Object."""

    type: Literal["refers"] = "refers"


class Triggers(BaseRelationship):
    """Subroutine triggers Subroutine."""

    type: Literal["triggers"] = "triggers"
