# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Literal, Required, TypedDict

from .shared_params.entity_data import EntityData
from .shared_params.customer_data import CustomerData

__all__ = ["ClientTrackParams"]


class ClientTrackParams(TypedDict, total=False):
    customer_id: Required[str]
    """ID which you provided when creating the customer"""

    customer_data: CustomerData
    """Additional customer properties.

    These will be used to create or update the customer if they don't exist or their
    properties are not already set.
    """

    entity_data: EntityData

    entity_id: str
    """
    If using [entity balances](/features/feature-entities) (eg, seats), the entity
    ID to track usage for.
    """

    event_name: str
    """
    An [event name](/features/tracking-usage#using-event-names) can be used in place
    of feature_id. This can be used if multiple features are tracked in the same
    event.
    """

    feature_id: str
    """ID of the feature to track usage for.

    Required if event_name is not provided. Use this for direct feature tracking.
    """

    idempotency_key: str
    """Unique key to prevent duplicate event recording.

    Use this to safely retry requests without creating duplicate usage records.
    """

    overage_behavior: Literal["cap", "reject"]
    """How to handle usage when balance is insufficient.

    'cap' limits usage to available balance, 'reject' prevents the usage entirely.
    """

    properties: Dict[str, object]
    """Additional properties to attach to this usage event."""

    skip_event: bool

    timestamp: float

    value: float
    """The amount of usage to record.

    Defaults to 1. Can be negative to increase the balance (e.g., when removing a
    seat).
    """
