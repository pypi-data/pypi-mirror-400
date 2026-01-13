# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = [
    "CheckResponse",
    "Balance",
    "BalanceReset",
    "BalanceBreakdown",
    "BalanceBreakdownReset",
    "BalanceFeature",
    "BalanceFeatureCreditSchema",
    "BalanceFeatureDisplay",
    "BalanceRollover",
    "Preview",
    "PreviewProduct",
    "PreviewProductFreeTrial",
    "PreviewProductItem",
    "PreviewProductItemConfig",
    "PreviewProductItemConfigRollover",
    "PreviewProductItemDisplay",
    "PreviewProductItemFeature",
    "PreviewProductItemFeatureCreditSchema",
    "PreviewProductItemFeatureDisplay",
    "PreviewProductItemTier",
    "PreviewProductProperties",
]


class BalanceReset(BaseModel):
    interval: Literal["one_off", "minute", "hour", "day", "week", "month", "quarter", "semi_annual", "year", "multiple"]

    resets_at: Optional[float] = None

    interval_count: Optional[float] = None


class BalanceBreakdownReset(BaseModel):
    interval: Literal["one_off", "minute", "hour", "day", "week", "month", "quarter", "semi_annual", "year", "multiple"]

    resets_at: Optional[float] = None

    interval_count: Optional[float] = None


class BalanceBreakdown(BaseModel):
    id: str

    current_balance: float

    granted_balance: float

    max_purchase: Optional[float] = None

    overage_allowed: bool

    plan_id: Optional[str] = None

    prepaid_quantity: float

    purchased_balance: float

    reset: Optional[BalanceBreakdownReset] = None

    usage: float


class BalanceFeatureCreditSchema(BaseModel):
    credit_cost: float

    metered_feature_id: str


class BalanceFeatureDisplay(BaseModel):
    plural: Optional[str] = None

    singular: Optional[str] = None


class BalanceFeature(BaseModel):
    id: str

    archived: bool

    consumable: bool

    name: str

    type: Literal["boolean", "metered", "credit_system"]

    credit_schema: Optional[List[BalanceFeatureCreditSchema]] = None

    display: Optional[BalanceFeatureDisplay] = None

    event_names: Optional[List[str]] = None


class BalanceRollover(BaseModel):
    balance: float

    expires_at: float


class Balance(BaseModel):
    current_balance: float

    feature_id: str

    granted_balance: float

    max_purchase: Optional[float] = None

    overage_allowed: bool

    plan_id: Optional[str] = None

    purchased_balance: float

    reset: Optional[BalanceReset] = None

    unlimited: bool

    usage: float

    breakdown: Optional[List[BalanceBreakdown]] = None

    feature: Optional[BalanceFeature] = None

    rollovers: Optional[List[BalanceRollover]] = None


class PreviewProductFreeTrial(BaseModel):
    """Free trial configuration for this product, if available"""

    card_required: bool
    """Whether the free trial requires a card.

    If false, the customer can attach the product without going through a checkout
    flow or having a card on file.
    """

    duration: Literal["day", "month", "year"]
    """The duration type of the free trial"""

    length: float
    """The length of the duration type specified"""

    trial_available: Optional[bool] = None
    """Used in customer context.

    Whether the free trial is available for the customer if they were to attach the
    product.
    """

    unique_fingerprint: bool
    """Whether the free trial is limited to one per customer fingerprint"""


class PreviewProductItemConfigRollover(BaseModel):
    duration: Literal["month", "forever"]

    length: float

    max: Optional[float] = None


class PreviewProductItemConfig(BaseModel):
    """Configuration for rollover and proration behavior of the feature."""

    on_decrease: Optional[Literal["prorate", "prorate_immediately", "prorate_next_cycle", "none", "no_prorations"]] = (
        None
    )

    on_increase: Optional[
        Literal["bill_immediately", "prorate_immediately", "prorate_next_cycle", "bill_next_cycle"]
    ] = None

    rollover: Optional[PreviewProductItemConfigRollover] = None


class PreviewProductItemDisplay(BaseModel):
    """The display of the product item."""

    primary_text: str

    secondary_text: Optional[str] = None


class PreviewProductItemFeatureCreditSchema(BaseModel):
    credit_cost: float
    """The credit cost of the metered feature."""

    metered_feature_id: str
    """The ID of the metered feature (should be a single_use feature)."""


class PreviewProductItemFeatureDisplay(BaseModel):
    """Singular and plural display names for the feature."""

    plural: str
    """The plural display name for the feature."""

    singular: str
    """The singular display name for the feature."""


class PreviewProductItemFeature(BaseModel):
    id: str
    """
    The ID of the feature, used to refer to it in other API calls like /track or
    /check.
    """

    type: Literal["static", "boolean", "single_use", "continuous_use", "credit_system"]
    """The type of the feature"""

    archived: Optional[bool] = None
    """Whether or not the feature is archived."""

    credit_schema: Optional[List[PreviewProductItemFeatureCreditSchema]] = None
    """Credit cost schema for credit system features."""

    display: Optional[PreviewProductItemFeatureDisplay] = None
    """Singular and plural display names for the feature."""

    name: Optional[str] = None
    """The name of the feature."""


class PreviewProductItemTier(BaseModel):
    amount: float
    """The price of the product item for this tier."""

    to: Union[float, Literal["inf"]]
    """The maximum amount of usage for this tier."""


class PreviewProductItem(BaseModel):
    """Product item defining features and pricing within a product"""

    billing_units: Optional[float] = None
    """The amount per billing unit (eg. $9 / 250 units)"""

    config: Optional[PreviewProductItemConfig] = None
    """Configuration for rollover and proration behavior of the feature."""

    display: Optional[PreviewProductItemDisplay] = None
    """The display of the product item."""

    entity_feature_id: Optional[str] = None
    """The entity feature ID of the product item if applicable."""

    feature: Optional[PreviewProductItemFeature] = None

    feature_id: Optional[str] = None
    """The feature ID of the product item.

    If the item is a fixed price, should be `null`
    """

    feature_type: Optional[Literal["single_use", "continuous_use", "boolean", "static"]] = None
    """Single use features are used once and then depleted, like API calls or credits.

    Continuous use features are those being used on an ongoing-basis, like storage
    or seats.
    """

    included_usage: Union[float, Literal["inf"], None] = None
    """The amount of usage included for this feature."""

    interval: Optional[Literal["minute", "hour", "day", "week", "month", "quarter", "semi_annual", "year"]] = None
    """The reset or billing interval of the product item.

    If null, feature will have no reset date, and if there's a price, it will be
    billed one-off.
    """

    interval_count: Optional[float] = None
    """The interval count of the product item."""

    next_cycle_quantity: Optional[float] = None
    """Used in customer context.

    Quantity of the feature the customer will prepay for in the next cycle.
    """

    price: Optional[float] = None
    """The price of the product item. Should be `null` if tiered pricing is set."""

    quantity: Optional[float] = None
    """Used in customer context. Quantity of the feature the customer has prepaid for."""

    reset_usage_when_enabled: Optional[bool] = None
    """Whether the usage should be reset when the product is enabled."""

    tiers: Optional[List[PreviewProductItemTier]] = None
    """Tiered pricing for the product item. Not applicable for fixed price items."""

    type: Optional[Literal["feature", "priced_feature", "price"]] = None
    """The type of the product item"""

    usage_model: Optional[Literal["prepaid", "pay_per_use"]] = None
    """
    Whether the feature should be prepaid upfront or billed for how much they use
    end of billing period.
    """


class PreviewProductProperties(BaseModel):
    is_free: bool
    """True if the product has no base price or usage prices"""

    is_one_off: bool
    """True if the product only contains a one-time price"""

    has_trial: Optional[bool] = None
    """True if the product includes a free trial"""

    interval_group: Optional[str] = None
    """The billing interval group for recurring products (e.g., 'monthly', 'yearly')"""

    updateable: Optional[bool] = None
    """
    True if the product can be updated after creation (only applicable if there are
    prepaid recurring prices)
    """


class PreviewProduct(BaseModel):
    id: str
    """The ID of the product you set when creating the product"""

    archived: bool
    """Whether this product has been archived and is no longer available"""

    base_variant_id: Optional[str] = None
    """ID of the base variant this product is derived from"""

    created_at: float
    """The timestamp of when the product was created in milliseconds since epoch"""

    env: Literal["sandbox", "live"]
    """The environment of the product"""

    free_trial: Optional[PreviewProductFreeTrial] = None
    """Free trial configuration for this product, if available"""

    group: Optional[str] = None
    """Product group which this product belongs to"""

    is_add_on: bool
    """Whether the product is an add-on and can be purchased alongside other products"""

    is_default: bool
    """Whether the product is the default product"""

    items: List[PreviewProductItem]
    """Array of product items that define the product's features and pricing"""

    name: str
    """The name of the product"""

    version: float
    """The current version of the product"""

    properties: Optional[PreviewProductProperties] = None

    scenario: Optional[
        Literal["scheduled", "active", "new", "renew", "upgrade", "downgrade", "cancel", "expired", "past_due"]
    ] = None
    """Scenario for when this product is used in attach flows"""


class Preview(BaseModel):
    feature_id: str

    feature_name: str

    message: str

    products: List[PreviewProduct]

    scenario: Literal["usage_limit", "feature_flag"]

    title: str


class CheckResponse(BaseModel):
    allowed: bool

    balance: Optional[Balance] = None

    customer_id: str

    entity_id: Optional[str] = None

    preview: Optional[Preview] = None

    required_balance: Optional[float] = None
