# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["ClientCancelParams"]


class ClientCancelParams(TypedDict, total=False):
    customer_id: Required[str]
    """The ID of the customer"""

    product_id: Required[str]
    """The ID of the product to cancel"""

    cancel_immediately: bool
    """Whether to cancel the product immediately or at period end"""

    entity_id: Optional[str]
    """The ID of the entity (optional)"""

    prorate: Optional[bool]
    """Whether to prorate the cancellation (defaults to true if not specified)"""
