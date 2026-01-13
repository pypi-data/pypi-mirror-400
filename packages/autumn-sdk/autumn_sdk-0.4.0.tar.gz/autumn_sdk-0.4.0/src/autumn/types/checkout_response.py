# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = [
    "CheckoutResponse",
    "Line",
    "LineItem",
    "LineItemConfig",
    "LineItemConfigRollover",
    "LineItemDisplay",
    "LineItemFeature",
    "LineItemFeatureCreditSchema",
    "LineItemFeatureDisplay",
    "LineItemTier",
    "CurrentProduct",
    "CurrentProductFreeTrial",
    "CurrentProductItem",
    "CurrentProductItemConfig",
    "CurrentProductItemConfigRollover",
    "CurrentProductItemDisplay",
    "CurrentProductItemFeature",
    "CurrentProductItemFeatureCreditSchema",
    "CurrentProductItemFeatureDisplay",
    "CurrentProductItemTier",
    "CurrentProductProperties",
    "NextCycle",
    "Option",
    "Product",
    "ProductFreeTrial",
    "ProductItem",
    "ProductItemConfig",
    "ProductItemConfigRollover",
    "ProductItemDisplay",
    "ProductItemFeature",
    "ProductItemFeatureCreditSchema",
    "ProductItemFeatureDisplay",
    "ProductItemTier",
    "ProductProperties",
]


class LineItemConfigRollover(BaseModel):
    duration: Literal["month", "forever"]

    length: float

    max: Optional[float] = None


class LineItemConfig(BaseModel):
    """Configuration for rollover and proration behavior of the feature."""

    on_decrease: Optional[Literal["prorate", "prorate_immediately", "prorate_next_cycle", "none", "no_prorations"]] = (
        None
    )

    on_increase: Optional[
        Literal["bill_immediately", "prorate_immediately", "prorate_next_cycle", "bill_next_cycle"]
    ] = None

    rollover: Optional[LineItemConfigRollover] = None


class LineItemDisplay(BaseModel):
    """The display of the product item."""

    primary_text: str

    secondary_text: Optional[str] = None


class LineItemFeatureCreditSchema(BaseModel):
    credit_cost: float
    """The credit cost of the metered feature."""

    metered_feature_id: str
    """The ID of the metered feature (should be a single_use feature)."""


class LineItemFeatureDisplay(BaseModel):
    """Singular and plural display names for the feature."""

    plural: str
    """The plural display name for the feature."""

    singular: str
    """The singular display name for the feature."""


class LineItemFeature(BaseModel):
    id: str
    """
    The ID of the feature, used to refer to it in other API calls like /track or
    /check.
    """

    type: Literal["static", "boolean", "single_use", "continuous_use", "credit_system"]
    """The type of the feature"""

    archived: Optional[bool] = None
    """Whether or not the feature is archived."""

    credit_schema: Optional[List[LineItemFeatureCreditSchema]] = None
    """Credit cost schema for credit system features."""

    display: Optional[LineItemFeatureDisplay] = None
    """Singular and plural display names for the feature."""

    name: Optional[str] = None
    """The name of the feature."""


class LineItemTier(BaseModel):
    amount: float
    """The price of the product item for this tier."""

    to: Union[float, Literal["inf"]]
    """The maximum amount of usage for this tier."""


class LineItem(BaseModel):
    """Product item defining features and pricing within a product"""

    billing_units: Optional[float] = None
    """The amount per billing unit (eg. $9 / 250 units)"""

    config: Optional[LineItemConfig] = None
    """Configuration for rollover and proration behavior of the feature."""

    display: Optional[LineItemDisplay] = None
    """The display of the product item."""

    entity_feature_id: Optional[str] = None
    """The entity feature ID of the product item if applicable."""

    feature: Optional[LineItemFeature] = None

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

    tiers: Optional[List[LineItemTier]] = None
    """Tiered pricing for the product item. Not applicable for fixed price items."""

    type: Optional[Literal["feature", "priced_feature", "price"]] = None
    """The type of the product item"""

    usage_model: Optional[Literal["prepaid", "pay_per_use"]] = None
    """
    Whether the feature should be prepaid upfront or billed for how much they use
    end of billing period.
    """


class Line(BaseModel):
    amount: float

    description: str

    item: Optional[LineItem] = None
    """Product item defining features and pricing within a product"""


class CurrentProductFreeTrial(BaseModel):
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


class CurrentProductItemConfigRollover(BaseModel):
    duration: Literal["month", "forever"]

    length: float

    max: Optional[float] = None


class CurrentProductItemConfig(BaseModel):
    """Configuration for rollover and proration behavior of the feature."""

    on_decrease: Optional[Literal["prorate", "prorate_immediately", "prorate_next_cycle", "none", "no_prorations"]] = (
        None
    )

    on_increase: Optional[
        Literal["bill_immediately", "prorate_immediately", "prorate_next_cycle", "bill_next_cycle"]
    ] = None

    rollover: Optional[CurrentProductItemConfigRollover] = None


class CurrentProductItemDisplay(BaseModel):
    """The display of the product item."""

    primary_text: str

    secondary_text: Optional[str] = None


class CurrentProductItemFeatureCreditSchema(BaseModel):
    credit_cost: float
    """The credit cost of the metered feature."""

    metered_feature_id: str
    """The ID of the metered feature (should be a single_use feature)."""


class CurrentProductItemFeatureDisplay(BaseModel):
    """Singular and plural display names for the feature."""

    plural: str
    """The plural display name for the feature."""

    singular: str
    """The singular display name for the feature."""


class CurrentProductItemFeature(BaseModel):
    id: str
    """
    The ID of the feature, used to refer to it in other API calls like /track or
    /check.
    """

    type: Literal["static", "boolean", "single_use", "continuous_use", "credit_system"]
    """The type of the feature"""

    archived: Optional[bool] = None
    """Whether or not the feature is archived."""

    credit_schema: Optional[List[CurrentProductItemFeatureCreditSchema]] = None
    """Credit cost schema for credit system features."""

    display: Optional[CurrentProductItemFeatureDisplay] = None
    """Singular and plural display names for the feature."""

    name: Optional[str] = None
    """The name of the feature."""


class CurrentProductItemTier(BaseModel):
    amount: float
    """The price of the product item for this tier."""

    to: Union[float, Literal["inf"]]
    """The maximum amount of usage for this tier."""


class CurrentProductItem(BaseModel):
    """Product item defining features and pricing within a product"""

    billing_units: Optional[float] = None
    """The amount per billing unit (eg. $9 / 250 units)"""

    config: Optional[CurrentProductItemConfig] = None
    """Configuration for rollover and proration behavior of the feature."""

    display: Optional[CurrentProductItemDisplay] = None
    """The display of the product item."""

    entity_feature_id: Optional[str] = None
    """The entity feature ID of the product item if applicable."""

    feature: Optional[CurrentProductItemFeature] = None

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

    tiers: Optional[List[CurrentProductItemTier]] = None
    """Tiered pricing for the product item. Not applicable for fixed price items."""

    type: Optional[Literal["feature", "priced_feature", "price"]] = None
    """The type of the product item"""

    usage_model: Optional[Literal["prepaid", "pay_per_use"]] = None
    """
    Whether the feature should be prepaid upfront or billed for how much they use
    end of billing period.
    """


class CurrentProductProperties(BaseModel):
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


class CurrentProduct(BaseModel):
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

    free_trial: Optional[CurrentProductFreeTrial] = None
    """Free trial configuration for this product, if available"""

    group: Optional[str] = None
    """Product group which this product belongs to"""

    is_add_on: bool
    """Whether the product is an add-on and can be purchased alongside other products"""

    is_default: bool
    """Whether the product is the default product"""

    items: List[CurrentProductItem]
    """Array of product items that define the product's features and pricing"""

    name: str
    """The name of the product"""

    version: float
    """The current version of the product"""

    properties: Optional[CurrentProductProperties] = None

    scenario: Optional[
        Literal["scheduled", "active", "new", "renew", "upgrade", "downgrade", "cancel", "expired", "past_due"]
    ] = None
    """Scenario for when this product is used in attach flows"""


class NextCycle(BaseModel):
    starts_at: float

    total: float


class Option(BaseModel):
    feature_id: str

    quantity: float

    adjustable_quantity: Optional[bool] = None

    internal_feature_id: Optional[str] = None

    upcoming_quantity: Optional[float] = None


class ProductFreeTrial(BaseModel):
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


class ProductItemConfigRollover(BaseModel):
    duration: Literal["month", "forever"]

    length: float

    max: Optional[float] = None


class ProductItemConfig(BaseModel):
    """Configuration for rollover and proration behavior of the feature."""

    on_decrease: Optional[Literal["prorate", "prorate_immediately", "prorate_next_cycle", "none", "no_prorations"]] = (
        None
    )

    on_increase: Optional[
        Literal["bill_immediately", "prorate_immediately", "prorate_next_cycle", "bill_next_cycle"]
    ] = None

    rollover: Optional[ProductItemConfigRollover] = None


class ProductItemDisplay(BaseModel):
    """The display of the product item."""

    primary_text: str

    secondary_text: Optional[str] = None


class ProductItemFeatureCreditSchema(BaseModel):
    credit_cost: float
    """The credit cost of the metered feature."""

    metered_feature_id: str
    """The ID of the metered feature (should be a single_use feature)."""


class ProductItemFeatureDisplay(BaseModel):
    """Singular and plural display names for the feature."""

    plural: str
    """The plural display name for the feature."""

    singular: str
    """The singular display name for the feature."""


class ProductItemFeature(BaseModel):
    id: str
    """
    The ID of the feature, used to refer to it in other API calls like /track or
    /check.
    """

    type: Literal["static", "boolean", "single_use", "continuous_use", "credit_system"]
    """The type of the feature"""

    archived: Optional[bool] = None
    """Whether or not the feature is archived."""

    credit_schema: Optional[List[ProductItemFeatureCreditSchema]] = None
    """Credit cost schema for credit system features."""

    display: Optional[ProductItemFeatureDisplay] = None
    """Singular and plural display names for the feature."""

    name: Optional[str] = None
    """The name of the feature."""


class ProductItemTier(BaseModel):
    amount: float
    """The price of the product item for this tier."""

    to: Union[float, Literal["inf"]]
    """The maximum amount of usage for this tier."""


class ProductItem(BaseModel):
    """Product item defining features and pricing within a product"""

    billing_units: Optional[float] = None
    """The amount per billing unit (eg. $9 / 250 units)"""

    config: Optional[ProductItemConfig] = None
    """Configuration for rollover and proration behavior of the feature."""

    display: Optional[ProductItemDisplay] = None
    """The display of the product item."""

    entity_feature_id: Optional[str] = None
    """The entity feature ID of the product item if applicable."""

    feature: Optional[ProductItemFeature] = None

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

    tiers: Optional[List[ProductItemTier]] = None
    """Tiered pricing for the product item. Not applicable for fixed price items."""

    type: Optional[Literal["feature", "priced_feature", "price"]] = None
    """The type of the product item"""

    usage_model: Optional[Literal["prepaid", "pay_per_use"]] = None
    """
    Whether the feature should be prepaid upfront or billed for how much they use
    end of billing period.
    """


class ProductProperties(BaseModel):
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


class Product(BaseModel):
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

    free_trial: Optional[ProductFreeTrial] = None
    """Free trial configuration for this product, if available"""

    group: Optional[str] = None
    """Product group which this product belongs to"""

    is_add_on: bool
    """Whether the product is an add-on and can be purchased alongside other products"""

    is_default: bool
    """Whether the product is the default product"""

    items: List[ProductItem]
    """Array of product items that define the product's features and pricing"""

    name: str
    """The name of the product"""

    version: float
    """The current version of the product"""

    properties: Optional[ProductProperties] = None

    scenario: Optional[
        Literal["scheduled", "active", "new", "renew", "upgrade", "downgrade", "cancel", "expired", "past_due"]
    ] = None
    """Scenario for when this product is used in attach flows"""


class CheckoutResponse(BaseModel):
    customer_id: str

    lines: List[Line]

    currency: Optional[str] = None

    current_product: Optional[CurrentProduct] = None

    has_prorations: Optional[bool] = None

    next_cycle: Optional[NextCycle] = None

    options: Optional[List[Option]] = None

    product: Optional[Product] = None

    total: Optional[float] = None

    url: Optional[str] = None
