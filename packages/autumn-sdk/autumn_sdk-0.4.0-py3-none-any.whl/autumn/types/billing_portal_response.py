# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["BillingPortalResponse"]


class BillingPortalResponse(BaseModel):
    customer_id: Optional[str] = None
    """The ID of the customer"""

    url: str
    """URL to the billing portal"""
