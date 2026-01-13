# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ClientBillingPortalParams"]


class ClientBillingPortalParams(TypedDict, total=False):
    configuration_id: str
    """Stripe billing portal configuration ID.

    Create configurations in your Stripe dashboard.
    """

    return_url: str
    """URL to redirect to when back button is clicked in the billing portal"""
