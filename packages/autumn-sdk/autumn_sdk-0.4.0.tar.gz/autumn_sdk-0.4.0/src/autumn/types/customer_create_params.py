# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Optional
from typing_extensions import Literal, Required, TypedDict

from .shared_params.entity_data import EntityData

__all__ = ["CustomerCreateParams"]


class CustomerCreateParams(TypedDict, total=False):
    id: Required[Optional[str]]
    """Your unique identifier for the customer"""

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

    with_autumn_id: bool

    disable_default: bool

    email: Optional[str]
    """Customer's email address"""

    entity_data: EntityData

    entity_id: str

    fingerprint: str
    """
    Unique identifier (eg, serial number) to detect duplicate customers and prevent
    free trial abuse
    """

    metadata: Optional[Dict[str, object]]
    """Additional metadata for the customer"""

    name: Optional[str]
    """Customer's name"""

    stripe_id: str
    """Stripe customer ID if you already have one"""
