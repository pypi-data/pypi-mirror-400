# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["SetupPaymentResponse"]


class SetupPaymentResponse(BaseModel):
    customer_id: str
    """The ID of the customer"""

    url: str
    """URL to the payment setup page"""
