# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["EntityData"]


class EntityData(TypedDict, total=False):
    feature_id: Required[str]
    """The feature ID that this entity is associated with"""

    name: str
    """Name of the entity"""
