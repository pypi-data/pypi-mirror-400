# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from autumn import Autumn, AsyncAutumn
from tests.utils import assert_matches_type
from autumn.types import (
    ReferralCreateCodeResponse,
    ReferralRedeemCodeResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestReferrals:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_code(self, client: Autumn) -> None:
        referral = client.referrals.create_code(
            customer_id="cus_123",
            program_id="prog_123",
        )
        assert_matches_type(ReferralCreateCodeResponse, referral, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_code(self, client: Autumn) -> None:
        response = client.referrals.with_raw_response.create_code(
            customer_id="cus_123",
            program_id="prog_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        referral = response.parse()
        assert_matches_type(ReferralCreateCodeResponse, referral, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_code(self, client: Autumn) -> None:
        with client.referrals.with_streaming_response.create_code(
            customer_id="cus_123",
            program_id="prog_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            referral = response.parse()
            assert_matches_type(ReferralCreateCodeResponse, referral, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_redeem_code(self, client: Autumn) -> None:
        referral = client.referrals.redeem_code(
            code="REF123ABC",
            customer_id="cus_456",
        )
        assert_matches_type(ReferralRedeemCodeResponse, referral, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_redeem_code(self, client: Autumn) -> None:
        response = client.referrals.with_raw_response.redeem_code(
            code="REF123ABC",
            customer_id="cus_456",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        referral = response.parse()
        assert_matches_type(ReferralRedeemCodeResponse, referral, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_redeem_code(self, client: Autumn) -> None:
        with client.referrals.with_streaming_response.redeem_code(
            code="REF123ABC",
            customer_id="cus_456",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            referral = response.parse()
            assert_matches_type(ReferralRedeemCodeResponse, referral, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncReferrals:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_code(self, async_client: AsyncAutumn) -> None:
        referral = await async_client.referrals.create_code(
            customer_id="cus_123",
            program_id="prog_123",
        )
        assert_matches_type(ReferralCreateCodeResponse, referral, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_code(self, async_client: AsyncAutumn) -> None:
        response = await async_client.referrals.with_raw_response.create_code(
            customer_id="cus_123",
            program_id="prog_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        referral = await response.parse()
        assert_matches_type(ReferralCreateCodeResponse, referral, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_code(self, async_client: AsyncAutumn) -> None:
        async with async_client.referrals.with_streaming_response.create_code(
            customer_id="cus_123",
            program_id="prog_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            referral = await response.parse()
            assert_matches_type(ReferralCreateCodeResponse, referral, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_redeem_code(self, async_client: AsyncAutumn) -> None:
        referral = await async_client.referrals.redeem_code(
            code="REF123ABC",
            customer_id="cus_456",
        )
        assert_matches_type(ReferralRedeemCodeResponse, referral, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_redeem_code(self, async_client: AsyncAutumn) -> None:
        response = await async_client.referrals.with_raw_response.redeem_code(
            code="REF123ABC",
            customer_id="cus_456",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        referral = await response.parse()
        assert_matches_type(ReferralRedeemCodeResponse, referral, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_redeem_code(self, async_client: AsyncAutumn) -> None:
        async with async_client.referrals.with_streaming_response.redeem_code(
            code="REF123ABC",
            customer_id="cus_456",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            referral = await response.parse()
            assert_matches_type(ReferralRedeemCodeResponse, referral, path=["response"])

        assert cast(Any, response.is_closed) is True
