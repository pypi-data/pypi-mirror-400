# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import typing

from .._models import BaseModel

__all__ = ["EventListResponse", "List"]


class List(BaseModel):
    id: str
    """Event ID (KSUID)"""

    customer_id: str
    """Customer identifier"""

    feature_id: str
    """ID of the feature that the event belongs to"""

    properties: object
    """Event properties (JSONB)"""

    timestamp: float
    """Event timestamp (epoch milliseconds)"""

    value: float
    """Event value/count"""


class EventListResponse(BaseModel):
    has_more: bool
    """Whether more results exist after this page"""

    limit: float
    """Limit passed in the request"""

    list: typing.List[List]
    """Array of items for current page"""

    offset: float
    """Current offset position"""

    total: float
    """Total number of items returned in the current page"""
