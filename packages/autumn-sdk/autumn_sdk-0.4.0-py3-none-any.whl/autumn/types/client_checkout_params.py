# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .._types import SequenceNotStr
from .shared_params.entity_data import EntityData
from .shared_params.customer_data import CustomerData

__all__ = [
    "ClientCheckoutParams",
    "FreeTrial",
    "FreeTrialFreeTrialConfig",
    "Item",
    "ItemConfig",
    "ItemConfigRollover",
    "ItemDisplay",
    "ItemFeature",
    "ItemFeatureCreditSchema",
    "ItemFeatureDisplay",
    "ItemTier",
    "Option",
]


class ClientCheckoutParams(TypedDict, total=False):
    customer_id: Required[str]

    billing_cycle_anchor: float

    checkout_session_params: object

    customer_data: Optional[CustomerData]
    """Customer details to set when creating a customer"""

    enable_product_immediately: bool

    entity_data: EntityData

    entity_id: Optional[str]

    finalize_invoice: bool

    force_checkout: bool

    free_trial: FreeTrial

    invoice: bool

    invoice_only: bool

    is_custom: bool

    items: Iterable[Item]

    metadata: object

    new_billing_subscription: bool

    options: Optional[Iterable[Option]]

    product_id: Optional[str]

    product_ids: Optional[SequenceNotStr[str]]

    reward: Union[str, SequenceNotStr[str]]

    setup_payment: bool

    success_url: str

    version: float


class FreeTrialFreeTrialConfig(TypedDict, total=False):
    length: Required[Union[str, float]]

    card_required: bool

    duration: Literal["day", "month", "year"]

    unique_fingerprint: bool


FreeTrial: TypeAlias = Union[FreeTrialFreeTrialConfig, bool]


class ItemConfigRollover(TypedDict, total=False):
    length: Required[float]

    max: Required[Optional[float]]

    duration: Literal["month", "forever"]


class ItemConfig(TypedDict, total=False):
    on_decrease: Optional[Literal["prorate", "prorate_immediately", "prorate_next_cycle", "none", "no_prorations"]]

    on_increase: Optional[Literal["bill_immediately", "prorate_immediately", "prorate_next_cycle", "bill_next_cycle"]]

    rollover: Optional[ItemConfigRollover]


class ItemDisplay(TypedDict, total=False):
    primary_text: Required[str]

    secondary_text: Optional[str]


class ItemFeatureCreditSchema(TypedDict, total=False):
    credit_cost: Required[float]
    """The credit cost of the metered feature."""

    metered_feature_id: Required[str]
    """The ID of the metered feature (should be a single_use feature)."""


class ItemFeatureDisplay(TypedDict, total=False):
    """Singular and plural display names for the feature."""

    plural: Required[str]
    """The plural display name for the feature."""

    singular: Required[str]
    """The singular display name for the feature."""


class ItemFeature(TypedDict, total=False):
    id: Required[str]
    """
    The ID of the feature, used to refer to it in other API calls like /track or
    /check.
    """

    type: Required[Literal["static", "boolean", "single_use", "continuous_use", "credit_system"]]
    """The type of the feature"""

    archived: Optional[bool]
    """Whether or not the feature is archived."""

    credit_schema: Optional[Iterable[ItemFeatureCreditSchema]]
    """Credit cost schema for credit system features."""

    display: Optional[ItemFeatureDisplay]
    """Singular and plural display names for the feature."""

    name: Optional[str]
    """The name of the feature."""


class ItemTier(TypedDict, total=False):
    amount: Required[float]
    """The price of the product item for this tier."""

    to: Required[Union[float, Literal["inf"]]]
    """The maximum amount of usage for this tier."""


class Item(TypedDict, total=False):
    interval: Required[Optional[Literal["minute", "hour", "day", "week", "month", "quarter", "semi_annual", "year"]]]
    """The reset or billing interval of the product item.

    If null, feature will have no reset date, and if there's a price, it will be
    billed one-off.
    """

    billing_units: Optional[float]
    """The billing units of the product item (eg $1 for 30 credits)."""

    config: Optional[ItemConfig]

    created_at: Optional[float]

    display: Optional[ItemDisplay]

    entitlement_id: Optional[str]

    entity_feature_id: Optional[str]
    """The feature ID of the entity (like seats) to track sub-balances for."""

    feature: Optional[ItemFeature]

    feature_id: Optional[str]
    """The feature ID of the product item. Should be null for fixed price items."""

    feature_type: Optional[Literal["single_use", "continuous_use", "boolean", "static"]]

    included_usage: Union[float, Literal["inf"], None]
    """The amount of usage included for this feature (per interval)."""

    interval_count: Optional[float]
    """Interval count of the feature."""

    price: Optional[float]
    """The price of the product item. Should be null if tiered pricing is set."""

    price_config: object

    price_id: Optional[str]

    reset_usage_when_enabled: Optional[bool]
    """Whether the usage should be reset when the product is enabled."""

    tiers: Optional[Iterable[ItemTier]]
    """Tiered pricing for the product item. Not applicable for fixed price items."""

    type: Optional[Literal["feature", "priced_feature", "price"]]
    """The type of the product item."""

    usage_limit: Optional[float]

    usage_model: Optional[Literal["prepaid", "pay_per_use"]]
    """
    Whether the feature should be prepaid upfront or billed for how much they use
    end of billing period.
    """


class Option(TypedDict, total=False):
    feature_id: Required[str]

    quantity: Required[float]

    adjustable_quantity: Optional[bool]

    internal_feature_id: Optional[str]

    upcoming_quantity: Optional[float]
