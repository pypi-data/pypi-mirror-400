"""Structure relationship models."""

from __future__ import annotations

from typing import Literal

from .._base import BaseRelationship


class ContainsImports(BaseRelationship):
    """Module contains_imports Module."""

    type: Literal["contains_imports"] = "contains_imports"


class DefinesAttribute(BaseRelationship):
    """Module/Class defines_attribute Attribute."""

    type: Literal["defines_attribute"] = "defines_attribute"


class DefinesMethod(BaseRelationship):
    """Class defines_method Subroutine."""

    type: Literal["defines_method"] = "defines_method"
