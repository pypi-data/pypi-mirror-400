# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import TypedDict

__all__ = ["CustomerUpdateParams"]


class CustomerUpdateParams(TypedDict, total=False):
    expand: str

    id: str
    """New unique identifier for the customer."""

    email: Optional[str]
    """Customer's email address"""

    fingerprint: Optional[str]
    """Unique identifier (eg, serial number) to detect duplicate customers."""

    metadata: Optional[Dict[str, object]]
    """
    Additional metadata for the customer (set individual keys to null to delete
    them).
    """

    name: Optional[str]
    """The customer's name."""

    stripe_id: Optional[str]
    """Stripe customer ID."""
