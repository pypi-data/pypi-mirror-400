# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Literal, Required, TypedDict

from .._types import SequenceNotStr

__all__ = ["ClientQueryParams"]


class ClientQueryParams(TypedDict, total=False):
    customer_id: Required[str]
    """The ID of the customer to query analytics for"""

    feature_id: Required[Union[str, SequenceNotStr[str]]]
    """The feature ID(s) to query"""

    range: Optional[Literal["24h", "7d", "30d", "90d", "last_cycle"]]
    """Time range for the query (defaults to last_cycle if not provided)"""
