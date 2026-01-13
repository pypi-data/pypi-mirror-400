# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = [
    "TrackResponse",
    "Balance",
    "BalanceReset",
    "BalanceBreakdown",
    "BalanceBreakdownReset",
    "BalanceFeature",
    "BalanceFeatureCreditSchema",
    "BalanceFeatureDisplay",
    "BalanceRollover",
    "Balances",
    "BalancesReset",
    "BalancesBreakdown",
    "BalancesBreakdownReset",
    "BalancesFeature",
    "BalancesFeatureCreditSchema",
    "BalancesFeatureDisplay",
    "BalancesRollover",
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


class TrackResponse(BaseModel):
    balance: Optional[Balance] = None

    customer_id: str
    """The ID of the customer"""

    value: float

    balances: Optional[Dict[str, Balances]] = None

    entity_id: Optional[str] = None
    """The ID of the entity (if provided)"""

    event_name: Optional[str] = None
    """The name of the event"""
