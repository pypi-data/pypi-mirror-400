"""Instance relationship models."""

from __future__ import annotations

from typing import Literal

from .._base import BaseRelationship


class CreatesInstance(BaseRelationship):
    """Module creates_instance Object."""

    type: Literal["creates_instance"] = "creates_instance"


class HasInstance(BaseRelationship):
    """Class has_instance Object."""

    type: Literal["has_instance"] = "has_instance"


class InstantiatesClass(BaseRelationship):
    """Subroutine instantiates_class Class."""

    type: Literal["instantiates_class"] = "instantiates_class"
