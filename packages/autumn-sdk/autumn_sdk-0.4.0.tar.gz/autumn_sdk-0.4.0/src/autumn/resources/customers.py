# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Iterable, Optional
from typing_extensions import Literal

import httpx

from ..types import customer_get_params, customer_list_params, customer_create_params, customer_update_params
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
from ..types.shared.customer import Customer
from ..types.customer_list_response import CustomerListResponse
from ..types.customer_delete_response import CustomerDeleteResponse
from ..types.shared_params.entity_data import EntityData

__all__ = ["CustomersResource", "AsyncCustomersResource"]


class CustomersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CustomersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/useautumn/py-sdk#accessing-raw-response-data-eg-headers
        """
        return CustomersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CustomersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/useautumn/py-sdk#with_streaming_response
        """
        return CustomersResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        id: Optional[str],
        expand: List[
            Literal[
                "invoices",
                "trials_used",
                "rewards",
                "entities",
                "referrals",
                "payment_method",
                "upcoming_invoice",
                "subscriptions.plan",
                "scheduled_subscriptions.plan",
                "balances.feature",
            ]
        ]
        | Omit = omit,
        with_autumn_id: bool | Omit = omit,
        disable_default: bool | Omit = omit,
        email: Optional[str] | Omit = omit,
        entity_data: EntityData | Omit = omit,
        entity_id: str | Omit = omit,
        fingerprint: str | Omit = omit,
        metadata: Optional[Dict[str, object]] | Omit = omit,
        name: Optional[str] | Omit = omit,
        stripe_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Customer:
        """
        Create Customer

        Args:
          id: Your unique identifier for the customer

          email: Customer's email address

          fingerprint: Unique identifier (eg, serial number) to detect duplicate customers and prevent
              free trial abuse

          metadata: Additional metadata for the customer

          name: Customer's name

          stripe_id: Stripe customer ID if you already have one

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/customers",
            body=maybe_transform(
                {
                    "id": id,
                    "disable_default": disable_default,
                    "email": email,
                    "entity_data": entity_data,
                    "entity_id": entity_id,
                    "fingerprint": fingerprint,
                    "metadata": metadata,
                    "name": name,
                    "stripe_id": stripe_id,
                },
                customer_create_params.CustomerCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "expand": expand,
                        "with_autumn_id": with_autumn_id,
                    },
                    customer_create_params.CustomerCreateParams,
                ),
            ),
            cast_to=Customer,
        )

    def update(
        self,
        customer_id: str,
        *,
        expand: str | Omit = omit,
        id: str | Omit = omit,
        email: Optional[str] | Omit = omit,
        fingerprint: Optional[str] | Omit = omit,
        metadata: Optional[Dict[str, object]] | Omit = omit,
        name: Optional[str] | Omit = omit,
        stripe_id: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Customer:
        """
        Update Customer

        Args:
          id: New unique identifier for the customer.

          email: Customer's email address

          fingerprint: Unique identifier (eg, serial number) to detect duplicate customers.

          metadata: Additional metadata for the customer (set individual keys to null to delete
              them).

          name: The customer's name.

          stripe_id: Stripe customer ID.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not customer_id:
            raise ValueError(f"Expected a non-empty value for `customer_id` but received {customer_id!r}")
        return self._post(
            f"/customers/{customer_id}",
            body=maybe_transform(
                {
                    "id": id,
                    "email": email,
                    "fingerprint": fingerprint,
                    "metadata": metadata,
                    "name": name,
                    "stripe_id": stripe_id,
                },
                customer_update_params.CustomerUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"expand": expand}, customer_update_params.CustomerUpdateParams),
            ),
            cast_to=Customer,
        )

    def list(
        self,
        *,
        limit: int | Omit = omit,
        offset: int | Omit = omit,
        plans: Iterable[customer_list_params.Plan] | Omit = omit,
        search: str | Omit = omit,
        subscription_status: Literal["active", "scheduled"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CustomerListResponse:
        """List Customers

        Args:
          limit: Number of items to return.

        Default 10, max 1000.

          offset: Number of items to skip

          plans: Filter by plan ID and version. Returns customers with active subscriptions to
              this plan.

          search: Search customers by id, name, or email

          subscription_status: Filter by customer product status. Defaults to active and scheduled

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/customers/list",
            body=maybe_transform(
                {
                    "limit": limit,
                    "offset": offset,
                    "plans": plans,
                    "search": search,
                    "subscription_status": subscription_status,
                },
                customer_list_params.CustomerListParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomerListResponse,
        )

    def delete(
        self,
        customer_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CustomerDeleteResponse:
        """
        Delete Customer

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not customer_id:
            raise ValueError(f"Expected a non-empty value for `customer_id` but received {customer_id!r}")
        return self._delete(
            f"/customers/{customer_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomerDeleteResponse,
        )

    def get(
        self,
        customer_id: str,
        *,
        expand: List[
            Literal[
                "invoices",
                "trials_used",
                "rewards",
                "entities",
                "referrals",
                "payment_method",
                "upcoming_invoice",
                "subscriptions.plan",
                "scheduled_subscriptions.plan",
                "balances.feature",
            ]
        ]
        | Omit = omit,
        skip_cache: bool | Omit = omit,
        with_autumn_id: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Customer:
        """
        Get Customer

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not customer_id:
            raise ValueError(f"Expected a non-empty value for `customer_id` but received {customer_id!r}")
        return self._get(
            f"/customers/{customer_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "expand": expand,
                        "skip_cache": skip_cache,
                        "with_autumn_id": with_autumn_id,
                    },
                    customer_get_params.CustomerGetParams,
                ),
            ),
            cast_to=Customer,
        )


class AsyncCustomersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCustomersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/useautumn/py-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncCustomersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCustomersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/useautumn/py-sdk#with_streaming_response
        """
        return AsyncCustomersResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        id: Optional[str],
        expand: List[
            Literal[
                "invoices",
                "trials_used",
                "rewards",
                "entities",
                "referrals",
                "payment_method",
                "upcoming_invoice",
                "subscriptions.plan",
                "scheduled_subscriptions.plan",
                "balances.feature",
            ]
        ]
        | Omit = omit,
        with_autumn_id: bool | Omit = omit,
        disable_default: bool | Omit = omit,
        email: Optional[str] | Omit = omit,
        entity_data: EntityData | Omit = omit,
        entity_id: str | Omit = omit,
        fingerprint: str | Omit = omit,
        metadata: Optional[Dict[str, object]] | Omit = omit,
        name: Optional[str] | Omit = omit,
        stripe_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Customer:
        """
        Create Customer

        Args:
          id: Your unique identifier for the customer

          email: Customer's email address

          fingerprint: Unique identifier (eg, serial number) to detect duplicate customers and prevent
              free trial abuse

          metadata: Additional metadata for the customer

          name: Customer's name

          stripe_id: Stripe customer ID if you already have one

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/customers",
            body=await async_maybe_transform(
                {
                    "id": id,
                    "disable_default": disable_default,
                    "email": email,
                    "entity_data": entity_data,
                    "entity_id": entity_id,
                    "fingerprint": fingerprint,
                    "metadata": metadata,
                    "name": name,
                    "stripe_id": stripe_id,
                },
                customer_create_params.CustomerCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "expand": expand,
                        "with_autumn_id": with_autumn_id,
                    },
                    customer_create_params.CustomerCreateParams,
                ),
            ),
            cast_to=Customer,
        )

    async def update(
        self,
        customer_id: str,
        *,
        expand: str | Omit = omit,
        id: str | Omit = omit,
        email: Optional[str] | Omit = omit,
        fingerprint: Optional[str] | Omit = omit,
        metadata: Optional[Dict[str, object]] | Omit = omit,
        name: Optional[str] | Omit = omit,
        stripe_id: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Customer:
        """
        Update Customer

        Args:
          id: New unique identifier for the customer.

          email: Customer's email address

          fingerprint: Unique identifier (eg, serial number) to detect duplicate customers.

          metadata: Additional metadata for the customer (set individual keys to null to delete
              them).

          name: The customer's name.

          stripe_id: Stripe customer ID.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not customer_id:
            raise ValueError(f"Expected a non-empty value for `customer_id` but received {customer_id!r}")
        return await self._post(
            f"/customers/{customer_id}",
            body=await async_maybe_transform(
                {
                    "id": id,
                    "email": email,
                    "fingerprint": fingerprint,
                    "metadata": metadata,
                    "name": name,
                    "stripe_id": stripe_id,
                },
                customer_update_params.CustomerUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"expand": expand}, customer_update_params.CustomerUpdateParams),
            ),
            cast_to=Customer,
        )

    async def list(
        self,
        *,
        limit: int | Omit = omit,
        offset: int | Omit = omit,
        plans: Iterable[customer_list_params.Plan] | Omit = omit,
        search: str | Omit = omit,
        subscription_status: Literal["active", "scheduled"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CustomerListResponse:
        """List Customers

        Args:
          limit: Number of items to return.

        Default 10, max 1000.

          offset: Number of items to skip

          plans: Filter by plan ID and version. Returns customers with active subscriptions to
              this plan.

          search: Search customers by id, name, or email

          subscription_status: Filter by customer product status. Defaults to active and scheduled

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/customers/list",
            body=await async_maybe_transform(
                {
                    "limit": limit,
                    "offset": offset,
                    "plans": plans,
                    "search": search,
                    "subscription_status": subscription_status,
                },
                customer_list_params.CustomerListParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomerListResponse,
        )

    async def delete(
        self,
        customer_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CustomerDeleteResponse:
        """
        Delete Customer

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not customer_id:
            raise ValueError(f"Expected a non-empty value for `customer_id` but received {customer_id!r}")
        return await self._delete(
            f"/customers/{customer_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CustomerDeleteResponse,
        )

    async def get(
        self,
        customer_id: str,
        *,
        expand: List[
            Literal[
                "invoices",
                "trials_used",
                "rewards",
                "entities",
                "referrals",
                "payment_method",
                "upcoming_invoice",
                "subscriptions.plan",
                "scheduled_subscriptions.plan",
                "balances.feature",
            ]
        ]
        | Omit = omit,
        skip_cache: bool | Omit = omit,
        with_autumn_id: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Customer:
        """
        Get Customer

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not customer_id:
            raise ValueError(f"Expected a non-empty value for `customer_id` but received {customer_id!r}")
        return await self._get(
            f"/customers/{customer_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "expand": expand,
                        "skip_cache": skip_cache,
                        "with_autumn_id": with_autumn_id,
                    },
                    customer_get_params.CustomerGetParams,
                ),
            ),
            cast_to=Customer,
        )


class CustomersResourceWithRawResponse:
    def __init__(self, customers: CustomersResource) -> None:
        self._customers = customers

        self.create = to_raw_response_wrapper(
            customers.create,
        )
        self.update = to_raw_response_wrapper(
            customers.update,
        )
        self.list = to_raw_response_wrapper(
            customers.list,
        )
        self.delete = to_raw_response_wrapper(
            customers.delete,
        )
        self.get = to_raw_response_wrapper(
            customers.get,
        )


class AsyncCustomersResourceWithRawResponse:
    def __init__(self, customers: AsyncCustomersResource) -> None:
        self._customers = customers

        self.create = async_to_raw_response_wrapper(
            customers.create,
        )
        self.update = async_to_raw_response_wrapper(
            customers.update,
        )
        self.list = async_to_raw_response_wrapper(
            customers.list,
        )
        self.delete = async_to_raw_response_wrapper(
            customers.delete,
        )
        self.get = async_to_raw_response_wrapper(
            customers.get,
        )


class CustomersResourceWithStreamingResponse:
    def __init__(self, customers: CustomersResource) -> None:
        self._customers = customers

        self.create = to_streamed_response_wrapper(
            customers.create,
        )
        self.update = to_streamed_response_wrapper(
            customers.update,
        )
        self.list = to_streamed_response_wrapper(
            customers.list,
        )
        self.delete = to_streamed_response_wrapper(
            customers.delete,
        )
        self.get = to_streamed_response_wrapper(
            customers.get,
        )


class AsyncCustomersResourceWithStreamingResponse:
    def __init__(self, customers: AsyncCustomersResource) -> None:
        self._customers = customers

        self.create = async_to_streamed_response_wrapper(
            customers.create,
        )
        self.update = async_to_streamed_response_wrapper(
            customers.update,
        )
        self.list = async_to_streamed_response_wrapper(
            customers.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            customers.delete,
        )
        self.get = async_to_streamed_response_wrapper(
            customers.get,
        )
