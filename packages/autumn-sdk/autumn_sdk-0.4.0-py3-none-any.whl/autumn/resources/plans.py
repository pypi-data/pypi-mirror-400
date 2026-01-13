# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional

import httpx

from ..types import plan_list_params, plan_create_params, plan_delete_params, plan_update_params
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
from ..types.shared.plan import Plan
from ..types.plan_list_response import PlanListResponse
from ..types.plan_delete_response import PlanDeleteResponse

__all__ = ["PlansResource", "AsyncPlansResource"]


class PlansResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PlansResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/useautumn/py-sdk#accessing-raw-response-data-eg-headers
        """
        return PlansResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PlansResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/useautumn/py-sdk#with_streaming_response
        """
        return PlansResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        id: str,
        name: str,
        add_on: bool | Omit = omit,
        default: bool | Omit = omit,
        description: Optional[str] | Omit = omit,
        features: Iterable[plan_create_params.Feature] | Omit = omit,
        free_trial: Optional[plan_create_params.FreeTrial] | Omit = omit,
        group: str | Omit = omit,
        price: plan_create_params.Price | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Plan:
        """
        Create Product

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/plans",
            body=maybe_transform(
                {
                    "id": id,
                    "name": name,
                    "add_on": add_on,
                    "default": default,
                    "description": description,
                    "features": features,
                    "free_trial": free_trial,
                    "group": group,
                    "price": price,
                },
                plan_create_params.PlanCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Plan,
        )

    def update(
        self,
        plan_id: str,
        *,
        id: str | Omit = omit,
        add_on: bool | Omit = omit,
        archived: bool | Omit = omit,
        default: bool | Omit = omit,
        description: Optional[str] | Omit = omit,
        features: Iterable[plan_update_params.Feature] | Omit = omit,
        free_trial: Optional[plan_update_params.FreeTrial] | Omit = omit,
        group: str | Omit = omit,
        name: str | Omit = omit,
        price: plan_update_params.Price | Omit = omit,
        version: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Plan:
        """
        Update Plan

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not plan_id:
            raise ValueError(f"Expected a non-empty value for `plan_id` but received {plan_id!r}")
        return self._post(
            f"/plans/{plan_id}",
            body=maybe_transform(
                {
                    "id": id,
                    "add_on": add_on,
                    "archived": archived,
                    "default": default,
                    "description": description,
                    "features": features,
                    "free_trial": free_trial,
                    "group": group,
                    "name": name,
                    "price": price,
                    "version": version,
                },
                plan_update_params.PlanUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Plan,
        )

    def list(
        self,
        *,
        customer_id: str | Omit = omit,
        entity_id: str | Omit = omit,
        include_archived: bool | Omit = omit,
        v1_schema: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PlanListResponse:
        """
        List Plans

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/plans",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "customer_id": customer_id,
                        "entity_id": entity_id,
                        "include_archived": include_archived,
                        "v1_schema": v1_schema,
                    },
                    plan_list_params.PlanListParams,
                ),
            ),
            cast_to=PlanListResponse,
        )

    def delete(
        self,
        plan_id: str,
        *,
        all_versions: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PlanDeleteResponse:
        """
        Delete Plan

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not plan_id:
            raise ValueError(f"Expected a non-empty value for `plan_id` but received {plan_id!r}")
        return self._delete(
            f"/plans/{plan_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"all_versions": all_versions}, plan_delete_params.PlanDeleteParams),
            ),
            cast_to=PlanDeleteResponse,
        )

    def get(
        self,
        plan_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Plan:
        """
        Get Plan

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not plan_id:
            raise ValueError(f"Expected a non-empty value for `plan_id` but received {plan_id!r}")
        return self._get(
            f"/plans/{plan_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Plan,
        )


class AsyncPlansResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPlansResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/useautumn/py-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncPlansResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPlansResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/useautumn/py-sdk#with_streaming_response
        """
        return AsyncPlansResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        id: str,
        name: str,
        add_on: bool | Omit = omit,
        default: bool | Omit = omit,
        description: Optional[str] | Omit = omit,
        features: Iterable[plan_create_params.Feature] | Omit = omit,
        free_trial: Optional[plan_create_params.FreeTrial] | Omit = omit,
        group: str | Omit = omit,
        price: plan_create_params.Price | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Plan:
        """
        Create Product

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/plans",
            body=await async_maybe_transform(
                {
                    "id": id,
                    "name": name,
                    "add_on": add_on,
                    "default": default,
                    "description": description,
                    "features": features,
                    "free_trial": free_trial,
                    "group": group,
                    "price": price,
                },
                plan_create_params.PlanCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Plan,
        )

    async def update(
        self,
        plan_id: str,
        *,
        id: str | Omit = omit,
        add_on: bool | Omit = omit,
        archived: bool | Omit = omit,
        default: bool | Omit = omit,
        description: Optional[str] | Omit = omit,
        features: Iterable[plan_update_params.Feature] | Omit = omit,
        free_trial: Optional[plan_update_params.FreeTrial] | Omit = omit,
        group: str | Omit = omit,
        name: str | Omit = omit,
        price: plan_update_params.Price | Omit = omit,
        version: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Plan:
        """
        Update Plan

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not plan_id:
            raise ValueError(f"Expected a non-empty value for `plan_id` but received {plan_id!r}")
        return await self._post(
            f"/plans/{plan_id}",
            body=await async_maybe_transform(
                {
                    "id": id,
                    "add_on": add_on,
                    "archived": archived,
                    "default": default,
                    "description": description,
                    "features": features,
                    "free_trial": free_trial,
                    "group": group,
                    "name": name,
                    "price": price,
                    "version": version,
                },
                plan_update_params.PlanUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Plan,
        )

    async def list(
        self,
        *,
        customer_id: str | Omit = omit,
        entity_id: str | Omit = omit,
        include_archived: bool | Omit = omit,
        v1_schema: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PlanListResponse:
        """
        List Plans

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/plans",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "customer_id": customer_id,
                        "entity_id": entity_id,
                        "include_archived": include_archived,
                        "v1_schema": v1_schema,
                    },
                    plan_list_params.PlanListParams,
                ),
            ),
            cast_to=PlanListResponse,
        )

    async def delete(
        self,
        plan_id: str,
        *,
        all_versions: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> PlanDeleteResponse:
        """
        Delete Plan

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not plan_id:
            raise ValueError(f"Expected a non-empty value for `plan_id` but received {plan_id!r}")
        return await self._delete(
            f"/plans/{plan_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"all_versions": all_versions}, plan_delete_params.PlanDeleteParams),
            ),
            cast_to=PlanDeleteResponse,
        )

    async def get(
        self,
        plan_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Plan:
        """
        Get Plan

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not plan_id:
            raise ValueError(f"Expected a non-empty value for `plan_id` but received {plan_id!r}")
        return await self._get(
            f"/plans/{plan_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Plan,
        )


class PlansResourceWithRawResponse:
    def __init__(self, plans: PlansResource) -> None:
        self._plans = plans

        self.create = to_raw_response_wrapper(
            plans.create,
        )
        self.update = to_raw_response_wrapper(
            plans.update,
        )
        self.list = to_raw_response_wrapper(
            plans.list,
        )
        self.delete = to_raw_response_wrapper(
            plans.delete,
        )
        self.get = to_raw_response_wrapper(
            plans.get,
        )


class AsyncPlansResourceWithRawResponse:
    def __init__(self, plans: AsyncPlansResource) -> None:
        self._plans = plans

        self.create = async_to_raw_response_wrapper(
            plans.create,
        )
        self.update = async_to_raw_response_wrapper(
            plans.update,
        )
        self.list = async_to_raw_response_wrapper(
            plans.list,
        )
        self.delete = async_to_raw_response_wrapper(
            plans.delete,
        )
        self.get = async_to_raw_response_wrapper(
            plans.get,
        )


class PlansResourceWithStreamingResponse:
    def __init__(self, plans: PlansResource) -> None:
        self._plans = plans

        self.create = to_streamed_response_wrapper(
            plans.create,
        )
        self.update = to_streamed_response_wrapper(
            plans.update,
        )
        self.list = to_streamed_response_wrapper(
            plans.list,
        )
        self.delete = to_streamed_response_wrapper(
            plans.delete,
        )
        self.get = to_streamed_response_wrapper(
            plans.get,
        )


class AsyncPlansResourceWithStreamingResponse:
    def __init__(self, plans: AsyncPlansResource) -> None:
        self._plans = plans

        self.create = async_to_streamed_response_wrapper(
            plans.create,
        )
        self.update = async_to_streamed_response_wrapper(
            plans.update,
        )
        self.list = async_to_streamed_response_wrapper(
            plans.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            plans.delete,
        )
        self.get = async_to_streamed_response_wrapper(
            plans.get,
        )
