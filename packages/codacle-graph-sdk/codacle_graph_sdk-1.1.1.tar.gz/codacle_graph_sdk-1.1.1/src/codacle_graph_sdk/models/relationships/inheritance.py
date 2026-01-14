"""Inheritance relationship models."""

from __future__ import annotations

from typing import Literal

from .._base import BaseRelationship


class InheritsFrom(BaseRelationship):
    """Class inherits_from Class."""

    type: Literal["inherits_from"] = "inherits_from"
