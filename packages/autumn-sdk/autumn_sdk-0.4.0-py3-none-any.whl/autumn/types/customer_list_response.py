# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel
from .shared.base_customer import BaseCustomer

__all__ = ["CustomerListResponse"]


class CustomerListResponse(BaseModel):
    has_more: bool
    """Whether more results exist after this page"""

    limit: float
    """Limit passed in the request"""

    list: List[BaseCustomer]
    """Array of items for current page"""

    offset: float
    """Current offset position"""

    total: float
    """Total number of items returned in the current page"""
