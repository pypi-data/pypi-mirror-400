# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["ReferralCreateCodeResponse"]


class ReferralCreateCodeResponse(BaseModel):
    """Referral code object returned by the API"""

    code: str
    """The referral code that can be shared with customers"""

    created_at: float
    """The timestamp of when the referral code was created"""

    customer_id: str
    """Your unique identifier for the customer"""
