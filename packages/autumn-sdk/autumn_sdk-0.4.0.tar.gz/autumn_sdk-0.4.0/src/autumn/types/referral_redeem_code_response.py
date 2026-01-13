# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["ReferralRedeemCodeResponse"]


class ReferralRedeemCodeResponse(BaseModel):
    """Redemption response object returned by the API"""

    id: str
    """The ID of the redemption event"""

    customer_id: str
    """Your unique identifier for the customer"""

    reward_id: str
    """The ID of the reward that will be granted"""
