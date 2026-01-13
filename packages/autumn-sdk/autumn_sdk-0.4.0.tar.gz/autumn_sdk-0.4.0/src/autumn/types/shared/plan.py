# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = [
    "Plan",
    "Feature",
    "FeaturePrice",
    "FeaturePriceTier",
    "FeatureReset",
    "FeatureDisplay",
    "FeatureFeature",
    "FeatureFeatureCreditSchema",
    "FeatureFeatureDisplay",
    "FeatureProration",
    "FeatureRollover",
    "Price",
    "PriceDisplay",
    "CustomerEligibility",
    "FreeTrial",
]


class FeaturePriceTier(BaseModel):
    amount: float

    to: Union[float, Literal["inf"]]


class FeaturePrice(BaseModel):
    billing_units: float

    interval: Literal["one_off", "week", "month", "quarter", "semi_annual", "year"]

    max_purchase: Optional[float] = None

    usage_model: Literal["prepaid", "pay_per_use"]

    amount: Optional[float] = None

    interval_count: Optional[float] = None

    tiers: Optional[List[FeaturePriceTier]] = None


class FeatureReset(BaseModel):
    interval: Literal["one_off", "minute", "hour", "day", "week", "month", "quarter", "semi_annual", "year"]

    reset_when_enabled: bool

    interval_count: Optional[float] = None


class FeatureDisplay(BaseModel):
    primary_text: str

    secondary_text: Optional[str] = None


class FeatureFeatureCreditSchema(BaseModel):
    credit_cost: float
    """The credit cost of the metered feature."""

    metered_feature_id: str
    """The ID of the metered feature (should be a single_use feature)."""


class FeatureFeatureDisplay(BaseModel):
    """Singular and plural display names for the feature."""

    plural: str
    """The plural display name for the feature."""

    singular: str
    """The singular display name for the feature."""


class FeatureFeature(BaseModel):
    id: str
    """
    The ID of the feature, used to refer to it in other API calls like /track or
    /check.
    """

    type: Literal["static", "boolean", "single_use", "continuous_use", "credit_system"]
    """The type of the feature"""

    archived: Optional[bool] = None
    """Whether or not the feature is archived."""

    credit_schema: Optional[List[FeatureFeatureCreditSchema]] = None
    """Credit cost schema for credit system features."""

    display: Optional[FeatureFeatureDisplay] = None
    """Singular and plural display names for the feature."""

    name: Optional[str] = None
    """The name of the feature."""


class FeatureProration(BaseModel):
    on_decrease: Optional[Literal["prorate", "prorate_immediately", "prorate_next_cycle", "none", "no_prorations"]] = (
        None
    )

    on_increase: Optional[
        Literal["bill_immediately", "prorate_immediately", "prorate_next_cycle", "bill_next_cycle"]
    ] = None


class FeatureRollover(BaseModel):
    expiry_duration_type: Literal["month", "forever"]

    max: Optional[float] = None

    expiry_duration_length: Optional[float] = None


class Feature(BaseModel):
    feature_id: str

    granted_balance: float

    price: Optional[FeaturePrice] = None

    reset: Optional[FeatureReset] = None

    unlimited: bool

    display: Optional[FeatureDisplay] = None

    feature: Optional[FeatureFeature] = None

    proration: Optional[FeatureProration] = None

    rollover: Optional[FeatureRollover] = None


class PriceDisplay(BaseModel):
    primary_text: str

    secondary_text: Optional[str] = None


class Price(BaseModel):
    amount: float

    interval: Literal["one_off", "week", "month", "quarter", "semi_annual", "year"]

    display: Optional[PriceDisplay] = None

    interval_count: Optional[float] = None


class CustomerEligibility(BaseModel):
    scenario: Literal["scheduled", "active", "new", "renew", "upgrade", "downgrade", "cancel", "expired", "past_due"]

    trial_available: Optional[bool] = None


class FreeTrial(BaseModel):
    card_required: bool

    duration_length: float

    duration_type: Literal["day", "month", "year"]


class Plan(BaseModel):
    id: str

    add_on: bool

    archived: bool

    base_variant_id: Optional[str] = None

    created_at: float

    default: bool

    description: Optional[str] = None

    env: Literal["sandbox", "live"]

    features: List[Feature]

    group: Optional[str] = None

    name: str

    price: Optional[Price] = None

    version: float

    customer_eligibility: Optional[CustomerEligibility] = None

    free_trial: Optional[FreeTrial] = None
