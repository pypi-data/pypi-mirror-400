# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["EntityData"]


class EntityData(BaseModel):
    feature_id: str
    """The feature ID that this entity is associated with"""

    name: Optional[str] = None
    """Name of the entity"""
