# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, Union, cast
from typing_extensions import Literal

import httpx

from ..types import event_list_params, event_aggregate_params
from .._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.event_list_response import EventListResponse
from ..types.event_aggregate_response import EventAggregateResponse

__all__ = ["EventsResource", "AsyncEventsResource"]


class EventsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EventsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/useautumn/py-sdk#accessing-raw-response-data-eg-headers
        """
        return EventsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EventsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/useautumn/py-sdk#with_streaming_response
        """
        return EventsResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        customer_id: str,
        feature_id: Union[str, SequenceNotStr[str]],
        custom_range: event_list_params.CustomRange | Omit = omit,
        limit: int | Omit = omit,
        offset: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EventListResponse:
        """
        List Events

        Args:
          customer_id: Filter events by customer ID

          feature_id: Filter by specific feature ID(s)

          custom_range: Filter events by time range

          limit: Number of items to return. Default 100, max 1000.

          offset: Number of items to skip

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/events/list",
            body=maybe_transform(
                {
                    "customer_id": customer_id,
                    "feature_id": feature_id,
                    "custom_range": custom_range,
                    "limit": limit,
                    "offset": offset,
                },
                event_list_params.EventListParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EventListResponse,
        )

    def aggregate(
        self,
        *,
        customer_id: str,
        feature_id: Union[str, SequenceNotStr[str]],
        bin_size: Literal["day", "hour"] | Omit = omit,
        custom_range: event_aggregate_params.CustomRange | Omit = omit,
        group_by: str | Omit = omit,
        range: Literal["24h", "7d", "30d", "90d", "last_cycle", "1bc", "3bc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EventAggregateResponse:
        """
        Aggregate Events

        Args:
          customer_id: Customer ID to aggregate events for

          feature_id: Feature ID(s) to aggregate events for

          bin_size: Size of the time bins to aggregate events for. Defaults to hour if range is 24h,
              otherwise day

          custom_range: Custom time range to aggregate events for. If provided, range must not be
              provided

          group_by: Property to group events by. If provided, each key in the response will be an
              object with distinct groups as the keys

          range: Time range to aggregate events for. Either range or custom_range must be
              provided

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return cast(
            EventAggregateResponse,
            self._post(
                "/events/aggregate",
                body=maybe_transform(
                    {
                        "customer_id": customer_id,
                        "feature_id": feature_id,
                        "bin_size": bin_size,
                        "custom_range": custom_range,
                        "group_by": group_by,
                        "range": range,
                    },
                    event_aggregate_params.EventAggregateParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, EventAggregateResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class AsyncEventsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEventsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/useautumn/py-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncEventsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEventsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/useautumn/py-sdk#with_streaming_response
        """
        return AsyncEventsResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        customer_id: str,
        feature_id: Union[str, SequenceNotStr[str]],
        custom_range: event_list_params.CustomRange | Omit = omit,
        limit: int | Omit = omit,
        offset: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EventListResponse:
        """
        List Events

        Args:
          customer_id: Filter events by customer ID

          feature_id: Filter by specific feature ID(s)

          custom_range: Filter events by time range

          limit: Number of items to return. Default 100, max 1000.

          offset: Number of items to skip

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/events/list",
            body=await async_maybe_transform(
                {
                    "customer_id": customer_id,
                    "feature_id": feature_id,
                    "custom_range": custom_range,
                    "limit": limit,
                    "offset": offset,
                },
                event_list_params.EventListParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EventListResponse,
        )

    async def aggregate(
        self,
        *,
        customer_id: str,
        feature_id: Union[str, SequenceNotStr[str]],
        bin_size: Literal["day", "hour"] | Omit = omit,
        custom_range: event_aggregate_params.CustomRange | Omit = omit,
        group_by: str | Omit = omit,
        range: Literal["24h", "7d", "30d", "90d", "last_cycle", "1bc", "3bc"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> EventAggregateResponse:
        """
        Aggregate Events

        Args:
          customer_id: Customer ID to aggregate events for

          feature_id: Feature ID(s) to aggregate events for

          bin_size: Size of the time bins to aggregate events for. Defaults to hour if range is 24h,
              otherwise day

          custom_range: Custom time range to aggregate events for. If provided, range must not be
              provided

          group_by: Property to group events by. If provided, each key in the response will be an
              object with distinct groups as the keys

          range: Time range to aggregate events for. Either range or custom_range must be
              provided

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return cast(
            EventAggregateResponse,
            await self._post(
                "/events/aggregate",
                body=await async_maybe_transform(
                    {
                        "customer_id": customer_id,
                        "feature_id": feature_id,
                        "bin_size": bin_size,
                        "custom_range": custom_range,
                        "group_by": group_by,
                        "range": range,
                    },
                    event_aggregate_params.EventAggregateParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, EventAggregateResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class EventsResourceWithRawResponse:
    def __init__(self, events: EventsResource) -> None:
        self._events = events

        self.list = to_raw_response_wrapper(
            events.list,
        )
        self.aggregate = to_raw_response_wrapper(
            events.aggregate,
        )


class AsyncEventsResourceWithRawResponse:
    def __init__(self, events: AsyncEventsResource) -> None:
        self._events = events

        self.list = async_to_raw_response_wrapper(
            events.list,
        )
        self.aggregate = async_to_raw_response_wrapper(
            events.aggregate,
        )


class EventsResourceWithStreamingResponse:
    def __init__(self, events: EventsResource) -> None:
        self._events = events

        self.list = to_streamed_response_wrapper(
            events.list,
        )
        self.aggregate = to_streamed_response_wrapper(
            events.aggregate,
        )


class AsyncEventsResourceWithStreamingResponse:
    def __init__(self, events: AsyncEventsResource) -> None:
        self._events = events

        self.list = async_to_streamed_response_wrapper(
            events.list,
        )
        self.aggregate = async_to_streamed_response_wrapper(
            events.aggregate,
        )
