# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import referral_create_code_params, referral_redeem_code_params
from .._types import Body, Query, Headers, NotGiven, not_given
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
from ..types.referral_create_code_response import ReferralCreateCodeResponse
from ..types.referral_redeem_code_response import ReferralRedeemCodeResponse

__all__ = ["ReferralsResource", "AsyncReferralsResource"]


class ReferralsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ReferralsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/useautumn/py-sdk#accessing-raw-response-data-eg-headers
        """
        return ReferralsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ReferralsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/useautumn/py-sdk#with_streaming_response
        """
        return ReferralsResourceWithStreamingResponse(self)

    def create_code(
        self,
        *,
        customer_id: str,
        program_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ReferralCreateCodeResponse:
        """
        Create a referral code

        Args:
          customer_id: The unique identifier of the customer

          program_id: ID of your referral program

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/referrals/code",
            body=maybe_transform(
                {
                    "customer_id": customer_id,
                    "program_id": program_id,
                },
                referral_create_code_params.ReferralCreateCodeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ReferralCreateCodeResponse,
        )

    def redeem_code(
        self,
        *,
        code: str,
        customer_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ReferralRedeemCodeResponse:
        """
        Redeem a referral code

        Args:
          code: The referral code to redeem

          customer_id: The unique identifier of the customer redeeming the code

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/referrals/redeem",
            body=maybe_transform(
                {
                    "code": code,
                    "customer_id": customer_id,
                },
                referral_redeem_code_params.ReferralRedeemCodeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ReferralRedeemCodeResponse,
        )


class AsyncReferralsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncReferralsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/useautumn/py-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncReferralsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncReferralsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/useautumn/py-sdk#with_streaming_response
        """
        return AsyncReferralsResourceWithStreamingResponse(self)

    async def create_code(
        self,
        *,
        customer_id: str,
        program_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ReferralCreateCodeResponse:
        """
        Create a referral code

        Args:
          customer_id: The unique identifier of the customer

          program_id: ID of your referral program

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/referrals/code",
            body=await async_maybe_transform(
                {
                    "customer_id": customer_id,
                    "program_id": program_id,
                },
                referral_create_code_params.ReferralCreateCodeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ReferralCreateCodeResponse,
        )

    async def redeem_code(
        self,
        *,
        code: str,
        customer_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ReferralRedeemCodeResponse:
        """
        Redeem a referral code

        Args:
          code: The referral code to redeem

          customer_id: The unique identifier of the customer redeeming the code

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/referrals/redeem",
            body=await async_maybe_transform(
                {
                    "code": code,
                    "customer_id": customer_id,
                },
                referral_redeem_code_params.ReferralRedeemCodeParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ReferralRedeemCodeResponse,
        )


class ReferralsResourceWithRawResponse:
    def __init__(self, referrals: ReferralsResource) -> None:
        self._referrals = referrals

        self.create_code = to_raw_response_wrapper(
            referrals.create_code,
        )
        self.redeem_code = to_raw_response_wrapper(
            referrals.redeem_code,
        )


class AsyncReferralsResourceWithRawResponse:
    def __init__(self, referrals: AsyncReferralsResource) -> None:
        self._referrals = referrals

        self.create_code = async_to_raw_response_wrapper(
            referrals.create_code,
        )
        self.redeem_code = async_to_raw_response_wrapper(
            referrals.redeem_code,
        )


class ReferralsResourceWithStreamingResponse:
    def __init__(self, referrals: ReferralsResource) -> None:
        self._referrals = referrals

        self.create_code = to_streamed_response_wrapper(
            referrals.create_code,
        )
        self.redeem_code = to_streamed_response_wrapper(
            referrals.redeem_code,
        )


class AsyncReferralsResourceWithStreamingResponse:
    def __init__(self, referrals: AsyncReferralsResource) -> None:
        self._referrals = referrals

        self.create_code = async_to_streamed_response_wrapper(
            referrals.create_code,
        )
        self.redeem_code = async_to_streamed_response_wrapper(
            referrals.redeem_code,
        )
