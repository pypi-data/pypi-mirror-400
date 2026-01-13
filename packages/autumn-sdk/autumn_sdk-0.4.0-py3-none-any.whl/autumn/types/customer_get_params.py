# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, TypedDict

__all__ = ["CustomerGetParams"]


class CustomerGetParams(TypedDict, total=False):
    expand: List[
        Literal[
            "invoices",
            "trials_used",
            "rewards",
            "entities",
            "referrals",
            "payment_method",
            "upcoming_invoice",
            "subscriptions.plan",
            "scheduled_subscriptions.plan",
            "balances.feature",
        ]
    ]

    skip_cache: bool

    with_autumn_id: bool
