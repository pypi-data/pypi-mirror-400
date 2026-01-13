# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from autumn import Autumn, AsyncAutumn
from tests.utils import assert_matches_type
from autumn.types import EntityDeleteResponse
from autumn.types.shared import Entity

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEntities:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Autumn) -> None:
        entity = client.entities.create(
            customer_id="customer_id",
            id="id",
            feature_id="feature_id",
        )
        assert_matches_type(Entity, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Autumn) -> None:
        entity = client.entities.create(
            customer_id="customer_id",
            id="id",
            feature_id="feature_id",
            customer_data={
                "disable_default": True,
                "email": "email",
                "fingerprint": "fingerprint",
                "metadata": {"foo": "bar"},
                "name": "name",
                "stripe_id": "stripe_id",
            },
            name="name",
        )
        assert_matches_type(Entity, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Autumn) -> None:
        response = client.entities.with_raw_response.create(
            customer_id="customer_id",
            id="id",
            feature_id="feature_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = response.parse()
        assert_matches_type(Entity, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Autumn) -> None:
        with client.entities.with_streaming_response.create(
            customer_id="customer_id",
            id="id",
            feature_id="feature_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = response.parse()
            assert_matches_type(Entity, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Autumn) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `customer_id` but received ''"):
            client.entities.with_raw_response.create(
                customer_id="",
                id="id",
                feature_id="feature_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Autumn) -> None:
        entity = client.entities.delete(
            entity_id="entity_id",
            customer_id="customer_id",
        )
        assert_matches_type(EntityDeleteResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Autumn) -> None:
        response = client.entities.with_raw_response.delete(
            entity_id="entity_id",
            customer_id="customer_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = response.parse()
        assert_matches_type(EntityDeleteResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Autumn) -> None:
        with client.entities.with_streaming_response.delete(
            entity_id="entity_id",
            customer_id="customer_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = response.parse()
            assert_matches_type(EntityDeleteResponse, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Autumn) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `customer_id` but received ''"):
            client.entities.with_raw_response.delete(
                entity_id="entity_id",
                customer_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `entity_id` but received ''"):
            client.entities.with_raw_response.delete(
                entity_id="",
                customer_id="customer_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Autumn) -> None:
        entity = client.entities.get(
            entity_id="entity_id",
            customer_id="customer_id",
        )
        assert_matches_type(Entity, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_with_all_params(self, client: Autumn) -> None:
        entity = client.entities.get(
            entity_id="entity_id",
            customer_id="customer_id",
            expand=["invoices"],
        )
        assert_matches_type(Entity, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Autumn) -> None:
        response = client.entities.with_raw_response.get(
            entity_id="entity_id",
            customer_id="customer_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = response.parse()
        assert_matches_type(Entity, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Autumn) -> None:
        with client.entities.with_streaming_response.get(
            entity_id="entity_id",
            customer_id="customer_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = response.parse()
            assert_matches_type(Entity, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Autumn) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `customer_id` but received ''"):
            client.entities.with_raw_response.get(
                entity_id="entity_id",
                customer_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `entity_id` but received ''"):
            client.entities.with_raw_response.get(
                entity_id="",
                customer_id="customer_id",
            )


class TestAsyncEntities:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncAutumn) -> None:
        entity = await async_client.entities.create(
            customer_id="customer_id",
            id="id",
            feature_id="feature_id",
        )
        assert_matches_type(Entity, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncAutumn) -> None:
        entity = await async_client.entities.create(
            customer_id="customer_id",
            id="id",
            feature_id="feature_id",
            customer_data={
                "disable_default": True,
                "email": "email",
                "fingerprint": "fingerprint",
                "metadata": {"foo": "bar"},
                "name": "name",
                "stripe_id": "stripe_id",
            },
            name="name",
        )
        assert_matches_type(Entity, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncAutumn) -> None:
        response = await async_client.entities.with_raw_response.create(
            customer_id="customer_id",
            id="id",
            feature_id="feature_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = await response.parse()
        assert_matches_type(Entity, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncAutumn) -> None:
        async with async_client.entities.with_streaming_response.create(
            customer_id="customer_id",
            id="id",
            feature_id="feature_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = await response.parse()
            assert_matches_type(Entity, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncAutumn) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `customer_id` but received ''"):
            await async_client.entities.with_raw_response.create(
                customer_id="",
                id="id",
                feature_id="feature_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncAutumn) -> None:
        entity = await async_client.entities.delete(
            entity_id="entity_id",
            customer_id="customer_id",
        )
        assert_matches_type(EntityDeleteResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncAutumn) -> None:
        response = await async_client.entities.with_raw_response.delete(
            entity_id="entity_id",
            customer_id="customer_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = await response.parse()
        assert_matches_type(EntityDeleteResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncAutumn) -> None:
        async with async_client.entities.with_streaming_response.delete(
            entity_id="entity_id",
            customer_id="customer_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = await response.parse()
            assert_matches_type(EntityDeleteResponse, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncAutumn) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `customer_id` but received ''"):
            await async_client.entities.with_raw_response.delete(
                entity_id="entity_id",
                customer_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `entity_id` but received ''"):
            await async_client.entities.with_raw_response.delete(
                entity_id="",
                customer_id="customer_id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncAutumn) -> None:
        entity = await async_client.entities.get(
            entity_id="entity_id",
            customer_id="customer_id",
        )
        assert_matches_type(Entity, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncAutumn) -> None:
        entity = await async_client.entities.get(
            entity_id="entity_id",
            customer_id="customer_id",
            expand=["invoices"],
        )
        assert_matches_type(Entity, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncAutumn) -> None:
        response = await async_client.entities.with_raw_response.get(
            entity_id="entity_id",
            customer_id="customer_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = await response.parse()
        assert_matches_type(Entity, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncAutumn) -> None:
        async with async_client.entities.with_streaming_response.get(
            entity_id="entity_id",
            customer_id="customer_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = await response.parse()
            assert_matches_type(Entity, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncAutumn) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `customer_id` but received ''"):
            await async_client.entities.with_raw_response.get(
                entity_id="entity_id",
                customer_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `entity_id` but received ''"):
            await async_client.entities.with_raw_response.get(
                entity_id="",
                customer_id="customer_id",
            )
