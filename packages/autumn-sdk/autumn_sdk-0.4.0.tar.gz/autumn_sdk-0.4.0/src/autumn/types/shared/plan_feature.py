# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = [
    "PlanFeature",
    "Price",
    "PriceTier",
    "Reset",
    "Display",
    "Feature",
    "FeatureCreditSchema",
    "FeatureDisplay",
    "Proration",
    "Rollover",
]


class PriceTier(BaseModel):
    amount: float

    to: Union[float, Literal["inf"]]


class Price(BaseModel):
    billing_units: float

    interval: Literal["one_off", "week", "month", "quarter", "semi_annual", "year"]

    max_purchase: Optional[float] = None

    usage_model: Literal["prepaid", "pay_per_use"]

    amount: Optional[float] = None

    interval_count: Optional[float] = None

    tiers: Optional[List[PriceTier]] = None


class Reset(BaseModel):
    interval: Literal["one_off", "minute", "hour", "day", "week", "month", "quarter", "semi_annual", "year"]

    reset_when_enabled: bool

    interval_count: Optional[float] = None


class Display(BaseModel):
    primary_text: str

    secondary_text: Optional[str] = None


class FeatureCreditSchema(BaseModel):
    credit_cost: float
    """The credit cost of the metered feature."""

    metered_feature_id: str
    """The ID of the metered feature (should be a single_use feature)."""


class FeatureDisplay(BaseModel):
    """Singular and plural display names for the feature."""

    plural: str
    """The plural display name for the feature."""

    singular: str
    """The singular display name for the feature."""


class Feature(BaseModel):
    id: str
    """
    The ID of the feature, used to refer to it in other API calls like /track or
    /check.
    """

    type: Literal["static", "boolean", "single_use", "continuous_use", "credit_system"]
    """The type of the feature"""

    archived: Optional[bool] = None
    """Whether or not the feature is archived."""

    credit_schema: Optional[List[FeatureCreditSchema]] = None
    """Credit cost schema for credit system features."""

    display: Optional[FeatureDisplay] = None
    """Singular and plural display names for the feature."""

    name: Optional[str] = None
    """The name of the feature."""


class Proration(BaseModel):
    on_decrease: Optional[Literal["prorate", "prorate_immediately", "prorate_next_cycle", "none", "no_prorations"]] = (
        None
    )

    on_increase: Optional[
        Literal["bill_immediately", "prorate_immediately", "prorate_next_cycle", "bill_next_cycle"]
    ] = None


class Rollover(BaseModel):
    expiry_duration_type: Literal["month", "forever"]

    max: Optional[float] = None

    expiry_duration_length: Optional[float] = None


class PlanFeature(BaseModel):
    """Plan feature object returned by the API"""

    feature_id: str

    granted_balance: float

    price: Optional[Price] = None

    reset: Optional[Reset] = None

    unlimited: bool

    display: Optional[Display] = None

    feature: Optional[Feature] = None

    proration: Optional[Proration] = None

    rollover: Optional[Rollover] = None
