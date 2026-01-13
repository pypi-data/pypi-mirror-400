# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["CancelResponse"]


class CancelResponse(BaseModel):
    customer_id: str
    """The ID of the customer"""

    product_id: str
    """The ID of the canceled product"""

    success: bool
    """Whether the cancellation was successful"""
