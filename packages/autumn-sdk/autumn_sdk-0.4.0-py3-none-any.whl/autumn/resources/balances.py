# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import balance_update_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
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
from ..types.balance_update_response import BalanceUpdateResponse

__all__ = ["BalancesResource", "AsyncBalancesResource"]


class BalancesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BalancesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/useautumn/py-sdk#accessing-raw-response-data-eg-headers
        """
        return BalancesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BalancesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/useautumn/py-sdk#with_streaming_response
        """
        return BalancesResourceWithStreamingResponse(self)

    def update(
        self,
        *,
        customer_id: str,
        feature_id: str,
        current_balance: float | Omit = omit,
        entity_id: str | Omit = omit,
        interval: Literal["one_off", "minute", "hour", "day", "week", "month", "quarter", "semi_annual", "year"]
        | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BalanceUpdateResponse:
        """Update or set the balance or usage for a specific feature for a customer.

        Either
        current_balance or usage must be provided, but not both.

        Args:
          customer_id: The ID of the customer.

          feature_id: The ID of the feature to update balance for.

          current_balance: The new balance value to set.

          entity_id: The ID of the entity to update balance for (if using entity balances).

          interval: The interval to update balance for.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/balances/update",
            body=maybe_transform(
                {
                    "customer_id": customer_id,
                    "feature_id": feature_id,
                    "current_balance": current_balance,
                    "entity_id": entity_id,
                    "interval": interval,
                },
                balance_update_params.BalanceUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BalanceUpdateResponse,
        )


class AsyncBalancesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBalancesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/useautumn/py-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncBalancesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBalancesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/useautumn/py-sdk#with_streaming_response
        """
        return AsyncBalancesResourceWithStreamingResponse(self)

    async def update(
        self,
        *,
        customer_id: str,
        feature_id: str,
        current_balance: float | Omit = omit,
        entity_id: str | Omit = omit,
        interval: Literal["one_off", "minute", "hour", "day", "week", "month", "quarter", "semi_annual", "year"]
        | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BalanceUpdateResponse:
        """Update or set the balance or usage for a specific feature for a customer.

        Either
        current_balance or usage must be provided, but not both.

        Args:
          customer_id: The ID of the customer.

          feature_id: The ID of the feature to update balance for.

          current_balance: The new balance value to set.

          entity_id: The ID of the entity to update balance for (if using entity balances).

          interval: The interval to update balance for.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/balances/update",
            body=await async_maybe_transform(
                {
                    "customer_id": customer_id,
                    "feature_id": feature_id,
                    "current_balance": current_balance,
                    "entity_id": entity_id,
                    "interval": interval,
                },
                balance_update_params.BalanceUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BalanceUpdateResponse,
        )


class BalancesResourceWithRawResponse:
    def __init__(self, balances: BalancesResource) -> None:
        self._balances = balances

        self.update = to_raw_response_wrapper(
            balances.update,
        )


class AsyncBalancesResourceWithRawResponse:
    def __init__(self, balances: AsyncBalancesResource) -> None:
        self._balances = balances

        self.update = async_to_raw_response_wrapper(
            balances.update,
        )


class BalancesResourceWithStreamingResponse:
    def __init__(self, balances: BalancesResource) -> None:
        self._balances = balances

        self.update = to_streamed_response_wrapper(
            balances.update,
        )


class AsyncBalancesResourceWithStreamingResponse:
    def __init__(self, balances: AsyncBalancesResource) -> None:
        self._balances = balances

        self.update = async_to_streamed_response_wrapper(
            balances.update,
        )
