# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypedDict

from .._types import SequenceNotStr

__all__ = ["EventAggregateParams", "CustomRange"]


class EventAggregateParams(TypedDict, total=False):
    customer_id: Required[str]
    """Customer ID to aggregate events for"""

    feature_id: Required[Union[str, SequenceNotStr[str]]]
    """Feature ID(s) to aggregate events for"""

    bin_size: Literal["day", "hour"]
    """Size of the time bins to aggregate events for.

    Defaults to hour if range is 24h, otherwise day
    """

    custom_range: CustomRange
    """Custom time range to aggregate events for.

    If provided, range must not be provided
    """

    group_by: str
    """Property to group events by.

    If provided, each key in the response will be an object with distinct groups as
    the keys
    """

    range: Literal["24h", "7d", "30d", "90d", "last_cycle", "1bc", "3bc"]
    """Time range to aggregate events for.

    Either range or custom_range must be provided
    """


class CustomRange(TypedDict, total=False):
    """Custom time range to aggregate events for.

    If provided, range must not be provided
    """

    end: Required[float]

    start: Required[float]
