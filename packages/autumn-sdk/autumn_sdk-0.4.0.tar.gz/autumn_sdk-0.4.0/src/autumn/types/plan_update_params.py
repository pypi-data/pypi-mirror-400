# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = [
    "PlanUpdateParams",
    "Feature",
    "FeaturePrice",
    "FeaturePriceTier",
    "FeatureProration",
    "FeatureReset",
    "FeatureRollover",
    "FreeTrial",
    "Price",
]


class PlanUpdateParams(TypedDict, total=False):
    id: str

    add_on: bool

    archived: bool

    default: bool

    description: Optional[str]

    features: Iterable[Feature]

    free_trial: Optional[FreeTrial]

    group: str

    name: str

    price: Price

    version: float


class FeaturePriceTier(TypedDict, total=False):
    amount: Required[float]

    to: Required[Union[float, Literal["inf"]]]


class FeaturePrice(TypedDict, total=False):
    interval: Required[Literal["one_off", "week", "month", "quarter", "semi_annual", "year"]]

    usage_model: Required[Literal["prepaid", "pay_per_use"]]

    amount: float

    billing_units: float

    interval_count: float

    max_purchase: float

    tiers: Iterable[FeaturePriceTier]


class FeatureProration(TypedDict, total=False):
    on_decrease: Required[Literal["prorate", "prorate_immediately", "prorate_next_cycle", "none", "no_prorations"]]

    on_increase: Required[Literal["bill_immediately", "prorate_immediately", "prorate_next_cycle", "bill_next_cycle"]]


class FeatureReset(TypedDict, total=False):
    interval: Required[Literal["one_off", "minute", "hour", "day", "week", "month", "quarter", "semi_annual", "year"]]

    interval_count: float

    reset_when_enabled: bool


class FeatureRollover(TypedDict, total=False):
    expiry_duration_type: Required[Literal["month", "forever"]]

    max: Required[float]

    expiry_duration_length: float


class Feature(TypedDict, total=False):
    feature_id: Required[str]

    granted_balance: float

    price: FeaturePrice

    proration: FeatureProration

    reset: FeatureReset

    rollover: FeatureRollover

    unlimited: bool


class FreeTrial(TypedDict, total=False):
    card_required: Required[bool]

    duration_length: Required[float]

    duration_type: Required[Literal["day", "month", "year"]]


class Price(TypedDict, total=False):
    amount: float

    interval: Literal["one_off", "week", "month", "quarter", "semi_annual", "year"]
