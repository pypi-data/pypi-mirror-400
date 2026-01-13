# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from autumn import Autumn, AsyncAutumn
from tests.utils import assert_matches_type
from autumn.types import EventListResponse, EventAggregateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEvents:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Autumn) -> None:
        event = client.events.list(
            customer_id="customer_id",
            feature_id="x",
        )
        assert_matches_type(EventListResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Autumn) -> None:
        event = client.events.list(
            customer_id="customer_id",
            feature_id="x",
            custom_range={
                "end": 0,
                "start": 0,
            },
            limit=1,
            offset=0,
        )
        assert_matches_type(EventListResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Autumn) -> None:
        response = client.events.with_raw_response.list(
            customer_id="customer_id",
            feature_id="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event = response.parse()
        assert_matches_type(EventListResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Autumn) -> None:
        with client.events.with_streaming_response.list(
            customer_id="customer_id",
            feature_id="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event = response.parse()
            assert_matches_type(EventListResponse, event, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_aggregate(self, client: Autumn) -> None:
        event = client.events.aggregate(
            customer_id="x",
            feature_id="x",
        )
        assert_matches_type(EventAggregateResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_aggregate_with_all_params(self, client: Autumn) -> None:
        event = client.events.aggregate(
            customer_id="x",
            feature_id="x",
            bin_size="day",
            custom_range={
                "end": 0,
                "start": 0,
            },
            group_by="properties.J!",
            range="24h",
        )
        assert_matches_type(EventAggregateResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_aggregate(self, client: Autumn) -> None:
        response = client.events.with_raw_response.aggregate(
            customer_id="x",
            feature_id="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event = response.parse()
        assert_matches_type(EventAggregateResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_aggregate(self, client: Autumn) -> None:
        with client.events.with_streaming_response.aggregate(
            customer_id="x",
            feature_id="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event = response.parse()
            assert_matches_type(EventAggregateResponse, event, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncEvents:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncAutumn) -> None:
        event = await async_client.events.list(
            customer_id="customer_id",
            feature_id="x",
        )
        assert_matches_type(EventListResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncAutumn) -> None:
        event = await async_client.events.list(
            customer_id="customer_id",
            feature_id="x",
            custom_range={
                "end": 0,
                "start": 0,
            },
            limit=1,
            offset=0,
        )
        assert_matches_type(EventListResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncAutumn) -> None:
        response = await async_client.events.with_raw_response.list(
            customer_id="customer_id",
            feature_id="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event = await response.parse()
        assert_matches_type(EventListResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncAutumn) -> None:
        async with async_client.events.with_streaming_response.list(
            customer_id="customer_id",
            feature_id="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event = await response.parse()
            assert_matches_type(EventListResponse, event, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_aggregate(self, async_client: AsyncAutumn) -> None:
        event = await async_client.events.aggregate(
            customer_id="x",
            feature_id="x",
        )
        assert_matches_type(EventAggregateResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_aggregate_with_all_params(self, async_client: AsyncAutumn) -> None:
        event = await async_client.events.aggregate(
            customer_id="x",
            feature_id="x",
            bin_size="day",
            custom_range={
                "end": 0,
                "start": 0,
            },
            group_by="properties.J!",
            range="24h",
        )
        assert_matches_type(EventAggregateResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_aggregate(self, async_client: AsyncAutumn) -> None:
        response = await async_client.events.with_raw_response.aggregate(
            customer_id="x",
            feature_id="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        event = await response.parse()
        assert_matches_type(EventAggregateResponse, event, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_aggregate(self, async_client: AsyncAutumn) -> None:
        async with async_client.events.with_streaming_response.aggregate(
            customer_id="x",
            feature_id="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            event = await response.parse()
            assert_matches_type(EventAggregateResponse, event, path=["response"])

        assert cast(Any, response.is_closed) is True
