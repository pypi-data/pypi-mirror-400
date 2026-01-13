# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["CustomerListParams", "Plan"]


class CustomerListParams(TypedDict, total=False):
    limit: int
    """Number of items to return. Default 10, max 1000."""

    offset: int
    """Number of items to skip"""

    plans: Iterable[Plan]
    """Filter by plan ID and version.

    Returns customers with active subscriptions to this plan.
    """

    search: str
    """Search customers by id, name, or email"""

    subscription_status: Literal["active", "scheduled"]
    """Filter by customer product status. Defaults to active and scheduled"""


class Plan(TypedDict, total=False):
    id: Required[str]

    versions: Iterable[float]
