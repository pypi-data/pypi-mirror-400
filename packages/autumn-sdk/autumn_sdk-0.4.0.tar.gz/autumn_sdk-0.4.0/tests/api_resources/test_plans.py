# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from autumn import Autumn, AsyncAutumn
from tests.utils import assert_matches_type
from autumn.types import (
    PlanListResponse,
    PlanDeleteResponse,
)
from autumn.types.shared import Plan

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPlans:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Autumn) -> None:
        plan = client.plans.create(
            id="id",
            name="name",
        )
        assert_matches_type(Plan, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Autumn) -> None:
        plan = client.plans.create(
            id="id",
            name="name",
            add_on=True,
            default=True,
            description="description",
            features=[
                {
                    "feature_id": "feature_id",
                    "granted_balance": 0,
                    "price": {
                        "interval": "one_off",
                        "usage_model": "prepaid",
                        "amount": 0,
                        "billing_units": 0,
                        "interval_count": 0,
                        "max_purchase": 0,
                        "tiers": [
                            {
                                "amount": 0,
                                "to": 0,
                            }
                        ],
                    },
                    "proration": {
                        "on_decrease": "prorate",
                        "on_increase": "bill_immediately",
                    },
                    "reset": {
                        "interval": "one_off",
                        "interval_count": 0,
                        "reset_when_enabled": True,
                    },
                    "rollover": {
                        "expiry_duration_type": "month",
                        "max": 0,
                        "expiry_duration_length": 0,
                    },
                    "unlimited": True,
                }
            ],
            free_trial={
                "card_required": True,
                "duration_length": 0,
                "duration_type": "day",
            },
            group="group",
            price={
                "amount": 0,
                "interval": "one_off",
            },
        )
        assert_matches_type(Plan, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Autumn) -> None:
        response = client.plans.with_raw_response.create(
            id="id",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        plan = response.parse()
        assert_matches_type(Plan, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Autumn) -> None:
        with client.plans.with_streaming_response.create(
            id="id",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            plan = response.parse()
            assert_matches_type(Plan, plan, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Autumn) -> None:
        plan = client.plans.update(
            plan_id="plan_id",
        )
        assert_matches_type(Plan, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Autumn) -> None:
        plan = client.plans.update(
            plan_id="plan_id",
            id="id",
            add_on=True,
            archived=True,
            default=True,
            description="description",
            features=[
                {
                    "feature_id": "feature_id",
                    "granted_balance": 0,
                    "price": {
                        "interval": "one_off",
                        "usage_model": "prepaid",
                        "amount": 0,
                        "billing_units": 0,
                        "interval_count": 0,
                        "max_purchase": 0,
                        "tiers": [
                            {
                                "amount": 0,
                                "to": 0,
                            }
                        ],
                    },
                    "proration": {
                        "on_decrease": "prorate",
                        "on_increase": "bill_immediately",
                    },
                    "reset": {
                        "interval": "one_off",
                        "interval_count": 0,
                        "reset_when_enabled": True,
                    },
                    "rollover": {
                        "expiry_duration_type": "month",
                        "max": 0,
                        "expiry_duration_length": 0,
                    },
                    "unlimited": True,
                }
            ],
            free_trial={
                "card_required": True,
                "duration_length": 0,
                "duration_type": "day",
            },
            group="group",
            name="name",
            price={
                "amount": 0,
                "interval": "one_off",
            },
            version=0,
        )
        assert_matches_type(Plan, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Autumn) -> None:
        response = client.plans.with_raw_response.update(
            plan_id="plan_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        plan = response.parse()
        assert_matches_type(Plan, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Autumn) -> None:
        with client.plans.with_streaming_response.update(
            plan_id="plan_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            plan = response.parse()
            assert_matches_type(Plan, plan, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Autumn) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `plan_id` but received ''"):
            client.plans.with_raw_response.update(
                plan_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Autumn) -> None:
        plan = client.plans.list()
        assert_matches_type(PlanListResponse, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Autumn) -> None:
        plan = client.plans.list(
            customer_id="customer_id",
            entity_id="entity_id",
            include_archived=True,
            v1_schema=True,
        )
        assert_matches_type(PlanListResponse, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Autumn) -> None:
        response = client.plans.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        plan = response.parse()
        assert_matches_type(PlanListResponse, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Autumn) -> None:
        with client.plans.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            plan = response.parse()
            assert_matches_type(PlanListResponse, plan, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Autumn) -> None:
        plan = client.plans.delete(
            plan_id="plan_id",
        )
        assert_matches_type(PlanDeleteResponse, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_with_all_params(self, client: Autumn) -> None:
        plan = client.plans.delete(
            plan_id="plan_id",
            all_versions=True,
        )
        assert_matches_type(PlanDeleteResponse, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Autumn) -> None:
        response = client.plans.with_raw_response.delete(
            plan_id="plan_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        plan = response.parse()
        assert_matches_type(PlanDeleteResponse, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Autumn) -> None:
        with client.plans.with_streaming_response.delete(
            plan_id="plan_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            plan = response.parse()
            assert_matches_type(PlanDeleteResponse, plan, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Autumn) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `plan_id` but received ''"):
            client.plans.with_raw_response.delete(
                plan_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get(self, client: Autumn) -> None:
        plan = client.plans.get(
            "plan_id",
        )
        assert_matches_type(Plan, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get(self, client: Autumn) -> None:
        response = client.plans.with_raw_response.get(
            "plan_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        plan = response.parse()
        assert_matches_type(Plan, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get(self, client: Autumn) -> None:
        with client.plans.with_streaming_response.get(
            "plan_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            plan = response.parse()
            assert_matches_type(Plan, plan, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get(self, client: Autumn) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `plan_id` but received ''"):
            client.plans.with_raw_response.get(
                "",
            )


class TestAsyncPlans:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncAutumn) -> None:
        plan = await async_client.plans.create(
            id="id",
            name="name",
        )
        assert_matches_type(Plan, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncAutumn) -> None:
        plan = await async_client.plans.create(
            id="id",
            name="name",
            add_on=True,
            default=True,
            description="description",
            features=[
                {
                    "feature_id": "feature_id",
                    "granted_balance": 0,
                    "price": {
                        "interval": "one_off",
                        "usage_model": "prepaid",
                        "amount": 0,
                        "billing_units": 0,
                        "interval_count": 0,
                        "max_purchase": 0,
                        "tiers": [
                            {
                                "amount": 0,
                                "to": 0,
                            }
                        ],
                    },
                    "proration": {
                        "on_decrease": "prorate",
                        "on_increase": "bill_immediately",
                    },
                    "reset": {
                        "interval": "one_off",
                        "interval_count": 0,
                        "reset_when_enabled": True,
                    },
                    "rollover": {
                        "expiry_duration_type": "month",
                        "max": 0,
                        "expiry_duration_length": 0,
                    },
                    "unlimited": True,
                }
            ],
            free_trial={
                "card_required": True,
                "duration_length": 0,
                "duration_type": "day",
            },
            group="group",
            price={
                "amount": 0,
                "interval": "one_off",
            },
        )
        assert_matches_type(Plan, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncAutumn) -> None:
        response = await async_client.plans.with_raw_response.create(
            id="id",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        plan = await response.parse()
        assert_matches_type(Plan, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncAutumn) -> None:
        async with async_client.plans.with_streaming_response.create(
            id="id",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            plan = await response.parse()
            assert_matches_type(Plan, plan, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncAutumn) -> None:
        plan = await async_client.plans.update(
            plan_id="plan_id",
        )
        assert_matches_type(Plan, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncAutumn) -> None:
        plan = await async_client.plans.update(
            plan_id="plan_id",
            id="id",
            add_on=True,
            archived=True,
            default=True,
            description="description",
            features=[
                {
                    "feature_id": "feature_id",
                    "granted_balance": 0,
                    "price": {
                        "interval": "one_off",
                        "usage_model": "prepaid",
                        "amount": 0,
                        "billing_units": 0,
                        "interval_count": 0,
                        "max_purchase": 0,
                        "tiers": [
                            {
                                "amount": 0,
                                "to": 0,
                            }
                        ],
                    },
                    "proration": {
                        "on_decrease": "prorate",
                        "on_increase": "bill_immediately",
                    },
                    "reset": {
                        "interval": "one_off",
                        "interval_count": 0,
                        "reset_when_enabled": True,
                    },
                    "rollover": {
                        "expiry_duration_type": "month",
                        "max": 0,
                        "expiry_duration_length": 0,
                    },
                    "unlimited": True,
                }
            ],
            free_trial={
                "card_required": True,
                "duration_length": 0,
                "duration_type": "day",
            },
            group="group",
            name="name",
            price={
                "amount": 0,
                "interval": "one_off",
            },
            version=0,
        )
        assert_matches_type(Plan, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncAutumn) -> None:
        response = await async_client.plans.with_raw_response.update(
            plan_id="plan_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        plan = await response.parse()
        assert_matches_type(Plan, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncAutumn) -> None:
        async with async_client.plans.with_streaming_response.update(
            plan_id="plan_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            plan = await response.parse()
            assert_matches_type(Plan, plan, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncAutumn) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `plan_id` but received ''"):
            await async_client.plans.with_raw_response.update(
                plan_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncAutumn) -> None:
        plan = await async_client.plans.list()
        assert_matches_type(PlanListResponse, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncAutumn) -> None:
        plan = await async_client.plans.list(
            customer_id="customer_id",
            entity_id="entity_id",
            include_archived=True,
            v1_schema=True,
        )
        assert_matches_type(PlanListResponse, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncAutumn) -> None:
        response = await async_client.plans.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        plan = await response.parse()
        assert_matches_type(PlanListResponse, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncAutumn) -> None:
        async with async_client.plans.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            plan = await response.parse()
            assert_matches_type(PlanListResponse, plan, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncAutumn) -> None:
        plan = await async_client.plans.delete(
            plan_id="plan_id",
        )
        assert_matches_type(PlanDeleteResponse, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_with_all_params(self, async_client: AsyncAutumn) -> None:
        plan = await async_client.plans.delete(
            plan_id="plan_id",
            all_versions=True,
        )
        assert_matches_type(PlanDeleteResponse, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncAutumn) -> None:
        response = await async_client.plans.with_raw_response.delete(
            plan_id="plan_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        plan = await response.parse()
        assert_matches_type(PlanDeleteResponse, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncAutumn) -> None:
        async with async_client.plans.with_streaming_response.delete(
            plan_id="plan_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            plan = await response.parse()
            assert_matches_type(PlanDeleteResponse, plan, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncAutumn) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `plan_id` but received ''"):
            await async_client.plans.with_raw_response.delete(
                plan_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get(self, async_client: AsyncAutumn) -> None:
        plan = await async_client.plans.get(
            "plan_id",
        )
        assert_matches_type(Plan, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncAutumn) -> None:
        response = await async_client.plans.with_raw_response.get(
            "plan_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        plan = await response.parse()
        assert_matches_type(Plan, plan, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncAutumn) -> None:
        async with async_client.plans.with_streaming_response.get(
            "plan_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            plan = await response.parse()
            assert_matches_type(Plan, plan, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get(self, async_client: AsyncAutumn) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `plan_id` but received ''"):
            await async_client.plans.with_raw_response.get(
                "",
            )
