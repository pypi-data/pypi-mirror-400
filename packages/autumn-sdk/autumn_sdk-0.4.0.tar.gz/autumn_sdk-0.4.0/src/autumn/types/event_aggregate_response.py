# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Union
from typing_extensions import TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "EventAggregateResponse",
    "EventAggregateResponseFlat",
    "EventAggregateResponseFlatList",
    "EventAggregateResponseFlatTotal",
    "EventAggregateResponseGrouped",
    "EventAggregateResponseGroupedList",
    "EventAggregateResponseGroupedTotal",
]


class EventAggregateResponseFlatList(BaseModel):
    period: float

    if TYPE_CHECKING:
        # Some versions of Pydantic <2.8.0 have a bug and don’t allow assigning a
        # value to this field, so for compatibility we avoid doing it at runtime.
        __pydantic_extra__: Dict[str, float] = FieldInfo(init=False)  # pyright: ignore[reportIncompatibleVariableOverride]

        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> float: ...
    else:
        __pydantic_extra__: Dict[str, float]


class EventAggregateResponseFlatTotal(BaseModel):
    count: float

    sum: float


class EventAggregateResponseFlat(BaseModel):
    """Response when group_by is not provided. Feature values are numbers."""

    list: List[EventAggregateResponseFlatList]

    total: Dict[str, EventAggregateResponseFlatTotal]


class EventAggregateResponseGroupedList(BaseModel):
    period: float

    if TYPE_CHECKING:
        # Some versions of Pydantic <2.8.0 have a bug and don’t allow assigning a
        # value to this field, so for compatibility we avoid doing it at runtime.
        __pydantic_extra__: Dict[str, Dict[str, float]] = FieldInfo(init=False)  # pyright: ignore[reportIncompatibleVariableOverride]

        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> Dict[str, float]: ...
    else:
        __pydantic_extra__: Dict[str, Dict[str, float]]


class EventAggregateResponseGroupedTotal(BaseModel):
    count: float

    sum: float


class EventAggregateResponseGrouped(BaseModel):
    """Response when group_by is provided.

    Feature values are objects with group values as keys.
    """

    list: List[EventAggregateResponseGroupedList]

    total: Dict[str, EventAggregateResponseGroupedTotal]


EventAggregateResponse: TypeAlias = Union[EventAggregateResponseFlat, EventAggregateResponseGrouped]
