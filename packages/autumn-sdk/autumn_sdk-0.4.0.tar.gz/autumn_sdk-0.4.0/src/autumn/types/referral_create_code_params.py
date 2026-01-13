# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ReferralCreateCodeParams"]


class ReferralCreateCodeParams(TypedDict, total=False):
    customer_id: Required[str]
    """The unique identifier of the customer"""

    program_id: Required[str]
    """ID of your referral program"""
