# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["BalanceUpdateParams"]


class BalanceUpdateParams(TypedDict, total=False):
    customer_id: Required[str]
    """The ID of the customer."""

    feature_id: Required[str]
    """The ID of the feature to update balance for."""

    current_balance: float
    """The new balance value to set."""

    entity_id: str
    """The ID of the entity to update balance for (if using entity balances)."""

    interval: Literal["one_off", "minute", "hour", "day", "week", "month", "quarter", "semi_annual", "year"]
    """The interval to update balance for."""
