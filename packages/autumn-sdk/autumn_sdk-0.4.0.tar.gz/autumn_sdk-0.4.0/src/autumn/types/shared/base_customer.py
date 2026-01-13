# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = [
    "BaseCustomer",
    "Balances",
    "BalancesReset",
    "BalancesBreakdown",
    "BalancesBreakdownReset",
    "BalancesFeature",
    "BalancesFeatureCreditSchema",
    "BalancesFeatureDisplay",
    "BalancesRollover",
    "ScheduledSubscription",
    "ScheduledSubscriptionPlan",
    "ScheduledSubscriptionPlanFeature",
    "ScheduledSubscriptionPlanFeaturePrice",
    "ScheduledSubscriptionPlanFeaturePriceTier",
    "ScheduledSubscriptionPlanFeatureReset",
    "ScheduledSubscriptionPlanFeatureDisplay",
    "ScheduledSubscriptionPlanFeatureFeature",
    "ScheduledSubscriptionPlanFeatureFeatureCreditSchema",
    "ScheduledSubscriptionPlanFeatureFeatureDisplay",
    "ScheduledSubscriptionPlanFeatureProration",
    "ScheduledSubscriptionPlanFeatureRollover",
    "ScheduledSubscriptionPlanPrice",
    "ScheduledSubscriptionPlanPriceDisplay",
    "ScheduledSubscriptionPlanCustomerEligibility",
    "ScheduledSubscriptionPlanFreeTrial",
    "Subscription",
    "SubscriptionPlan",
    "SubscriptionPlanFeature",
    "SubscriptionPlanFeaturePrice",
    "SubscriptionPlanFeaturePriceTier",
    "SubscriptionPlanFeatureReset",
    "SubscriptionPlanFeatureDisplay",
    "SubscriptionPlanFeatureFeature",
    "SubscriptionPlanFeatureFeatureCreditSchema",
    "SubscriptionPlanFeatureFeatureDisplay",
    "SubscriptionPlanFeatureProration",
    "SubscriptionPlanFeatureRollover",
    "SubscriptionPlanPrice",
    "SubscriptionPlanPriceDisplay",
    "SubscriptionPlanCustomerEligibility",
    "SubscriptionPlanFreeTrial",
]


class BalancesReset(BaseModel):
    interval: Literal["one_off", "minute", "hour", "day", "week", "month", "quarter", "semi_annual", "year", "multiple"]

    resets_at: Optional[float] = None

    interval_count: Optional[float] = None


class BalancesBreakdownReset(BaseModel):
    interval: Literal["one_off", "minute", "hour", "day", "week", "month", "quarter", "semi_annual", "year", "multiple"]

    resets_at: Optional[float] = None

    interval_count: Optional[float] = None


class BalancesBreakdown(BaseModel):
    id: str

    current_balance: float

    granted_balance: float

    max_purchase: Optional[float] = None

    overage_allowed: bool

    plan_id: Optional[str] = None

    prepaid_quantity: float

    purchased_balance: float

    reset: Optional[BalancesBreakdownReset] = None

    usage: float


class BalancesFeatureCreditSchema(BaseModel):
    credit_cost: float

    metered_feature_id: str


class BalancesFeatureDisplay(BaseModel):
    plural: Optional[str] = None

    singular: Optional[str] = None


class BalancesFeature(BaseModel):
    id: str

    archived: bool

    consumable: bool

    name: str

    type: Literal["boolean", "metered", "credit_system"]

    credit_schema: Optional[List[BalancesFeatureCreditSchema]] = None

    display: Optional[BalancesFeatureDisplay] = None

    event_names: Optional[List[str]] = None


class BalancesRollover(BaseModel):
    balance: float

    expires_at: float


class Balances(BaseModel):
    current_balance: float

    feature_id: str

    granted_balance: float

    max_purchase: Optional[float] = None

    overage_allowed: bool

    plan_id: Optional[str] = None

    purchased_balance: float

    reset: Optional[BalancesReset] = None

    unlimited: bool

    usage: float

    breakdown: Optional[List[BalancesBreakdown]] = None

    feature: Optional[BalancesFeature] = None

    rollovers: Optional[List[BalancesRollover]] = None


class ScheduledSubscriptionPlanFeaturePriceTier(BaseModel):
    amount: float

    to: Union[float, Literal["inf"]]


class ScheduledSubscriptionPlanFeaturePrice(BaseModel):
    billing_units: float

    interval: Literal["one_off", "week", "month", "quarter", "semi_annual", "year"]

    max_purchase: Optional[float] = None

    usage_model: Literal["prepaid", "pay_per_use"]

    amount: Optional[float] = None

    interval_count: Optional[float] = None

    tiers: Optional[List[ScheduledSubscriptionPlanFeaturePriceTier]] = None


class ScheduledSubscriptionPlanFeatureReset(BaseModel):
    interval: Literal["one_off", "minute", "hour", "day", "week", "month", "quarter", "semi_annual", "year"]

    reset_when_enabled: bool

    interval_count: Optional[float] = None


class ScheduledSubscriptionPlanFeatureDisplay(BaseModel):
    primary_text: str

    secondary_text: Optional[str] = None


class ScheduledSubscriptionPlanFeatureFeatureCreditSchema(BaseModel):
    credit_cost: float
    """The credit cost of the metered feature."""

    metered_feature_id: str
    """The ID of the metered feature (should be a single_use feature)."""


class ScheduledSubscriptionPlanFeatureFeatureDisplay(BaseModel):
    """Singular and plural display names for the feature."""

    plural: str
    """The plural display name for the feature."""

    singular: str
    """The singular display name for the feature."""


class ScheduledSubscriptionPlanFeatureFeature(BaseModel):
    id: str
    """
    The ID of the feature, used to refer to it in other API calls like /track or
    /check.
    """

    type: Literal["static", "boolean", "single_use", "continuous_use", "credit_system"]
    """The type of the feature"""

    archived: Optional[bool] = None
    """Whether or not the feature is archived."""

    credit_schema: Optional[List[ScheduledSubscriptionPlanFeatureFeatureCreditSchema]] = None
    """Credit cost schema for credit system features."""

    display: Optional[ScheduledSubscriptionPlanFeatureFeatureDisplay] = None
    """Singular and plural display names for the feature."""

    name: Optional[str] = None
    """The name of the feature."""


class ScheduledSubscriptionPlanFeatureProration(BaseModel):
    on_decrease: Optional[Literal["prorate", "prorate_immediately", "prorate_next_cycle", "none", "no_prorations"]] = (
        None
    )

    on_increase: Optional[
        Literal["bill_immediately", "prorate_immediately", "prorate_next_cycle", "bill_next_cycle"]
    ] = None


class ScheduledSubscriptionPlanFeatureRollover(BaseModel):
    expiry_duration_type: Literal["month", "forever"]

    max: Optional[float] = None

    expiry_duration_length: Optional[float] = None


class ScheduledSubscriptionPlanFeature(BaseModel):
    feature_id: str

    granted_balance: float

    price: Optional[ScheduledSubscriptionPlanFeaturePrice] = None

    reset: Optional[ScheduledSubscriptionPlanFeatureReset] = None

    unlimited: bool

    display: Optional[ScheduledSubscriptionPlanFeatureDisplay] = None

    feature: Optional[ScheduledSubscriptionPlanFeatureFeature] = None

    proration: Optional[ScheduledSubscriptionPlanFeatureProration] = None

    rollover: Optional[ScheduledSubscriptionPlanFeatureRollover] = None


class ScheduledSubscriptionPlanPriceDisplay(BaseModel):
    primary_text: str

    secondary_text: Optional[str] = None


class ScheduledSubscriptionPlanPrice(BaseModel):
    amount: float

    interval: Literal["one_off", "week", "month", "quarter", "semi_annual", "year"]

    display: Optional[ScheduledSubscriptionPlanPriceDisplay] = None

    interval_count: Optional[float] = None


class ScheduledSubscriptionPlanCustomerEligibility(BaseModel):
    scenario: Literal["scheduled", "active", "new", "renew", "upgrade", "downgrade", "cancel", "expired", "past_due"]

    trial_available: Optional[bool] = None


class ScheduledSubscriptionPlanFreeTrial(BaseModel):
    card_required: bool

    duration_length: float

    duration_type: Literal["day", "month", "year"]


class ScheduledSubscriptionPlan(BaseModel):
    id: str

    add_on: bool

    archived: bool

    base_variant_id: Optional[str] = None

    created_at: float

    default: bool

    description: Optional[str] = None

    env: Literal["sandbox", "live"]

    features: List[ScheduledSubscriptionPlanFeature]

    group: Optional[str] = None

    name: str

    price: Optional[ScheduledSubscriptionPlanPrice] = None

    version: float

    customer_eligibility: Optional[ScheduledSubscriptionPlanCustomerEligibility] = None

    free_trial: Optional[ScheduledSubscriptionPlanFreeTrial] = None


class ScheduledSubscription(BaseModel):
    add_on: bool

    canceled_at: Optional[float] = None

    current_period_end: Optional[float] = None

    current_period_start: Optional[float] = None

    default: bool

    expires_at: Optional[float] = None

    past_due: bool

    plan_id: str

    quantity: float

    started_at: float

    status: Literal["active", "scheduled", "expired"]

    trial_ends_at: Optional[float] = None

    plan: Optional[ScheduledSubscriptionPlan] = None


class SubscriptionPlanFeaturePriceTier(BaseModel):
    amount: float

    to: Union[float, Literal["inf"]]


class SubscriptionPlanFeaturePrice(BaseModel):
    billing_units: float

    interval: Literal["one_off", "week", "month", "quarter", "semi_annual", "year"]

    max_purchase: Optional[float] = None

    usage_model: Literal["prepaid", "pay_per_use"]

    amount: Optional[float] = None

    interval_count: Optional[float] = None

    tiers: Optional[List[SubscriptionPlanFeaturePriceTier]] = None


class SubscriptionPlanFeatureReset(BaseModel):
    interval: Literal["one_off", "minute", "hour", "day", "week", "month", "quarter", "semi_annual", "year"]

    reset_when_enabled: bool

    interval_count: Optional[float] = None


class SubscriptionPlanFeatureDisplay(BaseModel):
    primary_text: str

    secondary_text: Optional[str] = None


class SubscriptionPlanFeatureFeatureCreditSchema(BaseModel):
    credit_cost: float
    """The credit cost of the metered feature."""

    metered_feature_id: str
    """The ID of the metered feature (should be a single_use feature)."""


class SubscriptionPlanFeatureFeatureDisplay(BaseModel):
    """Singular and plural display names for the feature."""

    plural: str
    """The plural display name for the feature."""

    singular: str
    """The singular display name for the feature."""


class SubscriptionPlanFeatureFeature(BaseModel):
    id: str
    """
    The ID of the feature, used to refer to it in other API calls like /track or
    /check.
    """

    type: Literal["static", "boolean", "single_use", "continuous_use", "credit_system"]
    """The type of the feature"""

    archived: Optional[bool] = None
    """Whether or not the feature is archived."""

    credit_schema: Optional[List[SubscriptionPlanFeatureFeatureCreditSchema]] = None
    """Credit cost schema for credit system features."""

    display: Optional[SubscriptionPlanFeatureFeatureDisplay] = None
    """Singular and plural display names for the feature."""

    name: Optional[str] = None
    """The name of the feature."""


class SubscriptionPlanFeatureProration(BaseModel):
    on_decrease: Optional[Literal["prorate", "prorate_immediately", "prorate_next_cycle", "none", "no_prorations"]] = (
        None
    )

    on_increase: Optional[
        Literal["bill_immediately", "prorate_immediately", "prorate_next_cycle", "bill_next_cycle"]
    ] = None


class SubscriptionPlanFeatureRollover(BaseModel):
    expiry_duration_type: Literal["month", "forever"]

    max: Optional[float] = None

    expiry_duration_length: Optional[float] = None


class SubscriptionPlanFeature(BaseModel):
    feature_id: str

    granted_balance: float

    price: Optional[SubscriptionPlanFeaturePrice] = None

    reset: Optional[SubscriptionPlanFeatureReset] = None

    unlimited: bool

    display: Optional[SubscriptionPlanFeatureDisplay] = None

    feature: Optional[SubscriptionPlanFeatureFeature] = None

    proration: Optional[SubscriptionPlanFeatureProration] = None

    rollover: Optional[SubscriptionPlanFeatureRollover] = None


class SubscriptionPlanPriceDisplay(BaseModel):
    primary_text: str

    secondary_text: Optional[str] = None


class SubscriptionPlanPrice(BaseModel):
    amount: float

    interval: Literal["one_off", "week", "month", "quarter", "semi_annual", "year"]

    display: Optional[SubscriptionPlanPriceDisplay] = None

    interval_count: Optional[float] = None


class SubscriptionPlanCustomerEligibility(BaseModel):
    scenario: Literal["scheduled", "active", "new", "renew", "upgrade", "downgrade", "cancel", "expired", "past_due"]

    trial_available: Optional[bool] = None


class SubscriptionPlanFreeTrial(BaseModel):
    card_required: bool

    duration_length: float

    duration_type: Literal["day", "month", "year"]


class SubscriptionPlan(BaseModel):
    id: str

    add_on: bool

    archived: bool

    base_variant_id: Optional[str] = None

    created_at: float

    default: bool

    description: Optional[str] = None

    env: Literal["sandbox", "live"]

    features: List[SubscriptionPlanFeature]

    group: Optional[str] = None

    name: str

    price: Optional[SubscriptionPlanPrice] = None

    version: float

    customer_eligibility: Optional[SubscriptionPlanCustomerEligibility] = None

    free_trial: Optional[SubscriptionPlanFreeTrial] = None


class Subscription(BaseModel):
    add_on: bool

    canceled_at: Optional[float] = None

    current_period_end: Optional[float] = None

    current_period_start: Optional[float] = None

    default: bool

    expires_at: Optional[float] = None

    past_due: bool

    plan_id: str

    quantity: float

    started_at: float

    status: Literal["active", "scheduled", "expired"]

    trial_ends_at: Optional[float] = None

    plan: Optional[SubscriptionPlan] = None


class BaseCustomer(BaseModel):
    id: Optional[str] = None

    balances: Dict[str, Balances]

    created_at: float

    email: Optional[str] = None

    env: Literal["sandbox", "live"]

    fingerprint: Optional[str] = None

    metadata: Dict[str, object]

    name: Optional[str] = None

    scheduled_subscriptions: List[ScheduledSubscription]

    stripe_id: Optional[str] = None

    subscriptions: List[Subscription]

    autumn_id: Optional[str] = None
