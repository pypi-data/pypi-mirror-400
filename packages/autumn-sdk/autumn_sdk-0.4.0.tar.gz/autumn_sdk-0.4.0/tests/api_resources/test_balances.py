# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from autumn import Autumn, AsyncAutumn
from tests.utils import assert_matches_type
from autumn.types import BalanceUpdateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBalances:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Autumn) -> None:
        balance = client.balances.update(
            customer_id="customer_id",
            feature_id="feature_id",
        )
        assert_matches_type(BalanceUpdateResponse, balance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Autumn) -> None:
        balance = client.balances.update(
            customer_id="customer_id",
            feature_id="feature_id",
            current_balance=0,
            entity_id="entity_id",
            interval="one_off",
        )
        assert_matches_type(BalanceUpdateResponse, balance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Autumn) -> None:
        response = client.balances.with_raw_response.update(
            customer_id="customer_id",
            feature_id="feature_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        balance = response.parse()
        assert_matches_type(BalanceUpdateResponse, balance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Autumn) -> None:
        with client.balances.with_streaming_response.update(
            customer_id="customer_id",
            feature_id="feature_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            balance = response.parse()
            assert_matches_type(BalanceUpdateResponse, balance, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncBalances:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncAutumn) -> None:
        balance = await async_client.balances.update(
            customer_id="customer_id",
            feature_id="feature_id",
        )
        assert_matches_type(BalanceUpdateResponse, balance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncAutumn) -> None:
        balance = await async_client.balances.update(
            customer_id="customer_id",
            feature_id="feature_id",
            current_balance=0,
            entity_id="entity_id",
            interval="one_off",
        )
        assert_matches_type(BalanceUpdateResponse, balance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncAutumn) -> None:
        response = await async_client.balances.with_raw_response.update(
            customer_id="customer_id",
            feature_id="feature_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        balance = await response.parse()
        assert_matches_type(BalanceUpdateResponse, balance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncAutumn) -> None:
        async with async_client.balances.with_streaming_response.update(
            customer_id="customer_id",
            feature_id="feature_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            balance = await response.parse()
            assert_matches_type(BalanceUpdateResponse, balance, path=["response"])

        assert cast(Any, response.is_closed) is True
