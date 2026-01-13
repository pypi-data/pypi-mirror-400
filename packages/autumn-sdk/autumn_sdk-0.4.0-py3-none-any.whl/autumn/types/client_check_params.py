# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, TypedDict

from .shared_params.entity_data import EntityData
from .shared_params.customer_data import CustomerData

__all__ = ["ClientCheckParams"]


class ClientCheckParams(TypedDict, total=False):
    customer_id: Required[str]
    """ID which you provided when creating the customer"""

    feature_id: Required[str]
    """ID of the feature to check access to. Required if product_id is not provided."""

    customer_data: CustomerData
    """Properties used if customer is automatically created.

    Will also update if the name or email is not already set.
    """

    entity_data: EntityData

    entity_id: str
    """If using entity balances (eg, seats), the entity ID to check access for."""

    properties: Dict[str, object]

    required_balance: float
    """If you know the amount of the feature the end user is consuming in advance.

    If their balance is below this quantity, allowed will be false.
    """

    send_event: bool
    """If true, a usage event will be recorded together with checking access.

    The required_balance field will be used as the usage value.
    """

    with_preview: bool
    """
    If true, the response will include a preview object, which can be used to
    display information such as a paywall or upgrade confirmation.
    """
