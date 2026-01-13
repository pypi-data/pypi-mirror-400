# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ReferralRedeemCodeParams"]


class ReferralRedeemCodeParams(TypedDict, total=False):
    code: Required[str]
    """The referral code to redeem"""

    customer_id: Required[str]
    """The unique identifier of the customer redeeming the code"""
