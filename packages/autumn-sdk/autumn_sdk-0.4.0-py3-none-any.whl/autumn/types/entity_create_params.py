# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

from .shared_params.customer_data import CustomerData

__all__ = ["EntityCreateParams"]


class EntityCreateParams(TypedDict, total=False):
    id: Required[Optional[str]]
    """The ID of the entity"""

    feature_id: Required[str]
    """The ID of the feature this entity is associated with"""

    customer_data: CustomerData
    """Customer details to set when creating a customer"""

    name: Optional[str]
    """The name of the entity"""
