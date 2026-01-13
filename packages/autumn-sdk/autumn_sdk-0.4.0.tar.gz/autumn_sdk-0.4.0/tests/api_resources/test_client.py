# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from autumn import Autumn, AsyncAutumn
from tests.utils import assert_matches_type
from autumn.types import (
    CheckResponse,
    QueryResponse,
    TrackResponse,
    AttachResponse,
    CancelResponse,
    CheckoutResponse,
    SetupPaymentResponse,
    BillingPortalResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestClient:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_attach(self, client: Autumn) -> None:
        client_ = client.attach(
            customer_id="cus_123",
        )
        assert_matches_type(AttachResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_attach_with_all_params(self, client: Autumn) -> None:
        client_ = client.attach(
            customer_id="cus_123",
            billing_cycle_anchor=0,
            checkout_session_params={},
            customer_data={
                "disable_default": True,
                "email": "email",
                "fingerprint": "fingerprint",
                "metadata": {"foo": "bar"},
                "name": "name",
                "stripe_id": "stripe_id",
            },
            enable_product_immediately=True,
            entity_data={
                "feature_id": "feature_id",
                "name": "name",
            },
            entity_id="entity_id",
            finalize_invoice=True,
            force_checkout=True,
            free_trial={
                "length": "string",
                "card_required": True,
                "duration": "day",
                "unique_fingerprint": True,
            },
            invoice=True,
            invoice_only=True,
            is_custom=True,
            items=[
                {
                    "interval": "minute",
                    "billing_units": 0,
                    "config": {
                        "on_decrease": "prorate",
                        "on_increase": "bill_immediately",
                        "rollover": {
                            "length": 0,
                            "max": 0,
                            "duration": "month",
                        },
                    },
                    "created_at": 0,
                    "display": {
                        "primary_text": "primary_text",
                        "secondary_text": "secondary_text",
                    },
                    "entitlement_id": "entitlement_id",
                    "entity_feature_id": "entity_feature_id",
                    "feature": {
                        "id": "id",
                        "type": "static",
                        "archived": True,
                        "credit_schema": [
                            {
                                "credit_cost": 0,
                                "metered_feature_id": "metered_feature_id",
                            }
                        ],
                        "display": {
                            "plural": "plural",
                            "singular": "singular",
                        },
                        "name": "name",
                    },
                    "feature_id": "feature_id",
                    "feature_type": "single_use",
                    "included_usage": 0,
                    "interval_count": 0,
                    "price": 0,
                    "price_config": {},
                    "price_id": "price_id",
                    "reset_usage_when_enabled": True,
                    "tiers": [
                        {
                            "amount": 10,
                            "to": 100,
                        }
                    ],
                    "type": "feature",
                    "usage_limit": 0,
                    "usage_model": "prepaid",
                }
            ],
            metadata={},
            new_billing_subscription=True,
            options=[
                {
                    "feature_id": "feature_id",
                    "quantity": 0,
                    "adjustable_quantity": True,
                    "internal_feature_id": "internal_feature_id",
                    "upcoming_quantity": 0,
                }
            ],
            product_id="pro_plan",
            product_ids=["string"],
            reward="string",
            setup_payment=True,
            success_url="success_url",
            version=0,
        )
        assert_matches_type(AttachResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_attach(self, client: Autumn) -> None:
        response = client.with_raw_response.attach(
            customer_id="cus_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(AttachResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_attach(self, client: Autumn) -> None:
        with client.with_streaming_response.attach(
            customer_id="cus_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(AttachResponse, client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_billing_portal(self, client: Autumn) -> None:
        client_ = client.billing_portal(
            customer_id="customer_id",
        )
        assert_matches_type(BillingPortalResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_billing_portal_with_all_params(self, client: Autumn) -> None:
        client_ = client.billing_portal(
            customer_id="customer_id",
            configuration_id="configuration_id",
            return_url="return_url",
        )
        assert_matches_type(BillingPortalResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_billing_portal(self, client: Autumn) -> None:
        response = client.with_raw_response.billing_portal(
            customer_id="customer_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(BillingPortalResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_billing_portal(self, client: Autumn) -> None:
        with client.with_streaming_response.billing_portal(
            customer_id="customer_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(BillingPortalResponse, client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_billing_portal(self, client: Autumn) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `customer_id` but received ''"):
            client.with_raw_response.billing_portal(
                customer_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_cancel(self, client: Autumn) -> None:
        client_ = client.cancel(
            customer_id="cus_123",
            product_id="pro_plan",
        )
        assert_matches_type(CancelResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_cancel_with_all_params(self, client: Autumn) -> None:
        client_ = client.cancel(
            customer_id="cus_123",
            product_id="pro_plan",
            cancel_immediately=False,
            entity_id="entity_123",
            prorate=True,
        )
        assert_matches_type(CancelResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_cancel(self, client: Autumn) -> None:
        response = client.with_raw_response.cancel(
            customer_id="cus_123",
            product_id="pro_plan",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(CancelResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_cancel(self, client: Autumn) -> None:
        with client.with_streaming_response.cancel(
            customer_id="cus_123",
            product_id="pro_plan",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(CancelResponse, client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_check(self, client: Autumn) -> None:
        client_ = client.check(
            customer_id="customer_id",
            feature_id="feature_id",
        )
        assert_matches_type(CheckResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_check_with_all_params(self, client: Autumn) -> None:
        client_ = client.check(
            customer_id="customer_id",
            feature_id="feature_id",
            customer_data={
                "disable_default": True,
                "email": "email",
                "fingerprint": "fingerprint",
                "metadata": {"foo": "bar"},
                "name": "name",
                "stripe_id": "stripe_id",
            },
            entity_data={
                "feature_id": "feature_id",
                "name": "name",
            },
            entity_id="entity_id",
            properties={"foo": "bar"},
            required_balance=0,
            send_event=True,
            with_preview=True,
        )
        assert_matches_type(CheckResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_check(self, client: Autumn) -> None:
        response = client.with_raw_response.check(
            customer_id="customer_id",
            feature_id="feature_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(CheckResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_check(self, client: Autumn) -> None:
        with client.with_streaming_response.check(
            customer_id="customer_id",
            feature_id="feature_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(CheckResponse, client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_checkout(self, client: Autumn) -> None:
        client_ = client.checkout(
            customer_id="customer_id",
        )
        assert_matches_type(CheckoutResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_checkout_with_all_params(self, client: Autumn) -> None:
        client_ = client.checkout(
            customer_id="customer_id",
            billing_cycle_anchor=0,
            checkout_session_params={},
            customer_data={
                "disable_default": True,
                "email": "email",
                "fingerprint": "fingerprint",
                "metadata": {"foo": "bar"},
                "name": "name",
                "stripe_id": "stripe_id",
            },
            enable_product_immediately=True,
            entity_data={
                "feature_id": "feature_id",
                "name": "name",
            },
            entity_id="entity_id",
            finalize_invoice=True,
            force_checkout=True,
            free_trial={
                "length": "string",
                "card_required": True,
                "duration": "day",
                "unique_fingerprint": True,
            },
            invoice=True,
            invoice_only=True,
            is_custom=True,
            items=[
                {
                    "interval": "minute",
                    "billing_units": 0,
                    "config": {
                        "on_decrease": "prorate",
                        "on_increase": "bill_immediately",
                        "rollover": {
                            "length": 0,
                            "max": 0,
                            "duration": "month",
                        },
                    },
                    "created_at": 0,
                    "display": {
                        "primary_text": "primary_text",
                        "secondary_text": "secondary_text",
                    },
                    "entitlement_id": "entitlement_id",
                    "entity_feature_id": "entity_feature_id",
                    "feature": {
                        "id": "id",
                        "type": "static",
                        "archived": True,
                        "credit_schema": [
                            {
                                "credit_cost": 0,
                                "metered_feature_id": "metered_feature_id",
                            }
                        ],
                        "display": {
                            "plural": "plural",
                            "singular": "singular",
                        },
                        "name": "name",
                    },
                    "feature_id": "feature_id",
                    "feature_type": "single_use",
                    "included_usage": 0,
                    "interval_count": 0,
                    "price": 0,
                    "price_config": {},
                    "price_id": "price_id",
                    "reset_usage_when_enabled": True,
                    "tiers": [
                        {
                            "amount": 10,
                            "to": 100,
                        }
                    ],
                    "type": "feature",
                    "usage_limit": 0,
                    "usage_model": "prepaid",
                }
            ],
            metadata={},
            new_billing_subscription=True,
            options=[
                {
                    "feature_id": "feature_id",
                    "quantity": 0,
                    "adjustable_quantity": True,
                    "internal_feature_id": "internal_feature_id",
                    "upcoming_quantity": 0,
                }
            ],
            product_id="product_id",
            product_ids=["string"],
            reward="string",
            setup_payment=True,
            success_url="success_url",
            version=0,
        )
        assert_matches_type(CheckoutResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_checkout(self, client: Autumn) -> None:
        response = client.with_raw_response.checkout(
            customer_id="customer_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(CheckoutResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_checkout(self, client: Autumn) -> None:
        with client.with_streaming_response.checkout(
            customer_id="customer_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(CheckoutResponse, client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_query(self, client: Autumn) -> None:
        client_ = client.query(
            customer_id="cus_123",
            feature_id="api_calls",
        )
        assert_matches_type(QueryResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_query_with_all_params(self, client: Autumn) -> None:
        client_ = client.query(
            customer_id="cus_123",
            feature_id="api_calls",
            range="7d",
        )
        assert_matches_type(QueryResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_query(self, client: Autumn) -> None:
        response = client.with_raw_response.query(
            customer_id="cus_123",
            feature_id="api_calls",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(QueryResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_query(self, client: Autumn) -> None:
        with client.with_streaming_response.query(
            customer_id="cus_123",
            feature_id="api_calls",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(QueryResponse, client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_setup_payment(self, client: Autumn) -> None:
        client_ = client.setup_payment(
            customer_id="customer_id",
        )
        assert_matches_type(SetupPaymentResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_setup_payment_with_all_params(self, client: Autumn) -> None:
        client_ = client.setup_payment(
            customer_id="customer_id",
            checkout_session_params={"foo": "bar"},
            customer_data={
                "disable_default": True,
                "email": "email",
                "fingerprint": "fingerprint",
                "metadata": {"foo": "bar"},
                "name": "name",
                "stripe_id": "stripe_id",
            },
            success_url="success_url",
        )
        assert_matches_type(SetupPaymentResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_setup_payment(self, client: Autumn) -> None:
        response = client.with_raw_response.setup_payment(
            customer_id="customer_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(SetupPaymentResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_setup_payment(self, client: Autumn) -> None:
        with client.with_streaming_response.setup_payment(
            customer_id="customer_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(SetupPaymentResponse, client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_track(self, client: Autumn) -> None:
        client_ = client.track(
            customer_id="x",
        )
        assert_matches_type(TrackResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_track_with_all_params(self, client: Autumn) -> None:
        client_ = client.track(
            customer_id="x",
            customer_data={
                "disable_default": True,
                "email": "email",
                "fingerprint": "fingerprint",
                "metadata": {"foo": "bar"},
                "name": "name",
                "stripe_id": "stripe_id",
            },
            entity_data={
                "feature_id": "feature_id",
                "name": "name",
            },
            entity_id="entity_id",
            event_name="x",
            feature_id="feature_id",
            idempotency_key="idempotency_key",
            overage_behavior="cap",
            properties={"foo": "bar"},
            skip_event=True,
            timestamp=0,
            value=0,
        )
        assert_matches_type(TrackResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_track(self, client: Autumn) -> None:
        response = client.with_raw_response.track(
            customer_id="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(TrackResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_track(self, client: Autumn) -> None:
        with client.with_streaming_response.track(
            customer_id="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(TrackResponse, client_, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncClient:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_attach(self, async_client: AsyncAutumn) -> None:
        client = await async_client.attach(
            customer_id="cus_123",
        )
        assert_matches_type(AttachResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_attach_with_all_params(self, async_client: AsyncAutumn) -> None:
        client = await async_client.attach(
            customer_id="cus_123",
            billing_cycle_anchor=0,
            checkout_session_params={},
            customer_data={
                "disable_default": True,
                "email": "email",
                "fingerprint": "fingerprint",
                "metadata": {"foo": "bar"},
                "name": "name",
                "stripe_id": "stripe_id",
            },
            enable_product_immediately=True,
            entity_data={
                "feature_id": "feature_id",
                "name": "name",
            },
            entity_id="entity_id",
            finalize_invoice=True,
            force_checkout=True,
            free_trial={
                "length": "string",
                "card_required": True,
                "duration": "day",
                "unique_fingerprint": True,
            },
            invoice=True,
            invoice_only=True,
            is_custom=True,
            items=[
                {
                    "interval": "minute",
                    "billing_units": 0,
                    "config": {
                        "on_decrease": "prorate",
                        "on_increase": "bill_immediately",
                        "rollover": {
                            "length": 0,
                            "max": 0,
                            "duration": "month",
                        },
                    },
                    "created_at": 0,
                    "display": {
                        "primary_text": "primary_text",
                        "secondary_text": "secondary_text",
                    },
                    "entitlement_id": "entitlement_id",
                    "entity_feature_id": "entity_feature_id",
                    "feature": {
                        "id": "id",
                        "type": "static",
                        "archived": True,
                        "credit_schema": [
                            {
                                "credit_cost": 0,
                                "metered_feature_id": "metered_feature_id",
                            }
                        ],
                        "display": {
                            "plural": "plural",
                            "singular": "singular",
                        },
                        "name": "name",
                    },
                    "feature_id": "feature_id",
                    "feature_type": "single_use",
                    "included_usage": 0,
                    "interval_count": 0,
                    "price": 0,
                    "price_config": {},
                    "price_id": "price_id",
                    "reset_usage_when_enabled": True,
                    "tiers": [
                        {
                            "amount": 10,
                            "to": 100,
                        }
                    ],
                    "type": "feature",
                    "usage_limit": 0,
                    "usage_model": "prepaid",
                }
            ],
            metadata={},
            new_billing_subscription=True,
            options=[
                {
                    "feature_id": "feature_id",
                    "quantity": 0,
                    "adjustable_quantity": True,
                    "internal_feature_id": "internal_feature_id",
                    "upcoming_quantity": 0,
                }
            ],
            product_id="pro_plan",
            product_ids=["string"],
            reward="string",
            setup_payment=True,
            success_url="success_url",
            version=0,
        )
        assert_matches_type(AttachResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_attach(self, async_client: AsyncAutumn) -> None:
        response = await async_client.with_raw_response.attach(
            customer_id="cus_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(AttachResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_attach(self, async_client: AsyncAutumn) -> None:
        async with async_client.with_streaming_response.attach(
            customer_id="cus_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(AttachResponse, client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_billing_portal(self, async_client: AsyncAutumn) -> None:
        client = await async_client.billing_portal(
            customer_id="customer_id",
        )
        assert_matches_type(BillingPortalResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_billing_portal_with_all_params(self, async_client: AsyncAutumn) -> None:
        client = await async_client.billing_portal(
            customer_id="customer_id",
            configuration_id="configuration_id",
            return_url="return_url",
        )
        assert_matches_type(BillingPortalResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_billing_portal(self, async_client: AsyncAutumn) -> None:
        response = await async_client.with_raw_response.billing_portal(
            customer_id="customer_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(BillingPortalResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_billing_portal(self, async_client: AsyncAutumn) -> None:
        async with async_client.with_streaming_response.billing_portal(
            customer_id="customer_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(BillingPortalResponse, client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_billing_portal(self, async_client: AsyncAutumn) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `customer_id` but received ''"):
            await async_client.with_raw_response.billing_portal(
                customer_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_cancel(self, async_client: AsyncAutumn) -> None:
        client = await async_client.cancel(
            customer_id="cus_123",
            product_id="pro_plan",
        )
        assert_matches_type(CancelResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_cancel_with_all_params(self, async_client: AsyncAutumn) -> None:
        client = await async_client.cancel(
            customer_id="cus_123",
            product_id="pro_plan",
            cancel_immediately=False,
            entity_id="entity_123",
            prorate=True,
        )
        assert_matches_type(CancelResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncAutumn) -> None:
        response = await async_client.with_raw_response.cancel(
            customer_id="cus_123",
            product_id="pro_plan",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(CancelResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncAutumn) -> None:
        async with async_client.with_streaming_response.cancel(
            customer_id="cus_123",
            product_id="pro_plan",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(CancelResponse, client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_check(self, async_client: AsyncAutumn) -> None:
        client = await async_client.check(
            customer_id="customer_id",
            feature_id="feature_id",
        )
        assert_matches_type(CheckResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_check_with_all_params(self, async_client: AsyncAutumn) -> None:
        client = await async_client.check(
            customer_id="customer_id",
            feature_id="feature_id",
            customer_data={
                "disable_default": True,
                "email": "email",
                "fingerprint": "fingerprint",
                "metadata": {"foo": "bar"},
                "name": "name",
                "stripe_id": "stripe_id",
            },
            entity_data={
                "feature_id": "feature_id",
                "name": "name",
            },
            entity_id="entity_id",
            properties={"foo": "bar"},
            required_balance=0,
            send_event=True,
            with_preview=True,
        )
        assert_matches_type(CheckResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_check(self, async_client: AsyncAutumn) -> None:
        response = await async_client.with_raw_response.check(
            customer_id="customer_id",
            feature_id="feature_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(CheckResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_check(self, async_client: AsyncAutumn) -> None:
        async with async_client.with_streaming_response.check(
            customer_id="customer_id",
            feature_id="feature_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(CheckResponse, client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_checkout(self, async_client: AsyncAutumn) -> None:
        client = await async_client.checkout(
            customer_id="customer_id",
        )
        assert_matches_type(CheckoutResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_checkout_with_all_params(self, async_client: AsyncAutumn) -> None:
        client = await async_client.checkout(
            customer_id="customer_id",
            billing_cycle_anchor=0,
            checkout_session_params={},
            customer_data={
                "disable_default": True,
                "email": "email",
                "fingerprint": "fingerprint",
                "metadata": {"foo": "bar"},
                "name": "name",
                "stripe_id": "stripe_id",
            },
            enable_product_immediately=True,
            entity_data={
                "feature_id": "feature_id",
                "name": "name",
            },
            entity_id="entity_id",
            finalize_invoice=True,
            force_checkout=True,
            free_trial={
                "length": "string",
                "card_required": True,
                "duration": "day",
                "unique_fingerprint": True,
            },
            invoice=True,
            invoice_only=True,
            is_custom=True,
            items=[
                {
                    "interval": "minute",
                    "billing_units": 0,
                    "config": {
                        "on_decrease": "prorate",
                        "on_increase": "bill_immediately",
                        "rollover": {
                            "length": 0,
                            "max": 0,
                            "duration": "month",
                        },
                    },
                    "created_at": 0,
                    "display": {
                        "primary_text": "primary_text",
                        "secondary_text": "secondary_text",
                    },
                    "entitlement_id": "entitlement_id",
                    "entity_feature_id": "entity_feature_id",
                    "feature": {
                        "id": "id",
                        "type": "static",
                        "archived": True,
                        "credit_schema": [
                            {
                                "credit_cost": 0,
                                "metered_feature_id": "metered_feature_id",
                            }
                        ],
                        "display": {
                            "plural": "plural",
                            "singular": "singular",
                        },
                        "name": "name",
                    },
                    "feature_id": "feature_id",
                    "feature_type": "single_use",
                    "included_usage": 0,
                    "interval_count": 0,
                    "price": 0,
                    "price_config": {},
                    "price_id": "price_id",
                    "reset_usage_when_enabled": True,
                    "tiers": [
                        {
                            "amount": 10,
                            "to": 100,
                        }
                    ],
                    "type": "feature",
                    "usage_limit": 0,
                    "usage_model": "prepaid",
                }
            ],
            metadata={},
            new_billing_subscription=True,
            options=[
                {
                    "feature_id": "feature_id",
                    "quantity": 0,
                    "adjustable_quantity": True,
                    "internal_feature_id": "internal_feature_id",
                    "upcoming_quantity": 0,
                }
            ],
            product_id="product_id",
            product_ids=["string"],
            reward="string",
            setup_payment=True,
            success_url="success_url",
            version=0,
        )
        assert_matches_type(CheckoutResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_checkout(self, async_client: AsyncAutumn) -> None:
        response = await async_client.with_raw_response.checkout(
            customer_id="customer_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(CheckoutResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_checkout(self, async_client: AsyncAutumn) -> None:
        async with async_client.with_streaming_response.checkout(
            customer_id="customer_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(CheckoutResponse, client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_query(self, async_client: AsyncAutumn) -> None:
        client = await async_client.query(
            customer_id="cus_123",
            feature_id="api_calls",
        )
        assert_matches_type(QueryResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_query_with_all_params(self, async_client: AsyncAutumn) -> None:
        client = await async_client.query(
            customer_id="cus_123",
            feature_id="api_calls",
            range="7d",
        )
        assert_matches_type(QueryResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_query(self, async_client: AsyncAutumn) -> None:
        response = await async_client.with_raw_response.query(
            customer_id="cus_123",
            feature_id="api_calls",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(QueryResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_query(self, async_client: AsyncAutumn) -> None:
        async with async_client.with_streaming_response.query(
            customer_id="cus_123",
            feature_id="api_calls",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(QueryResponse, client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_setup_payment(self, async_client: AsyncAutumn) -> None:
        client = await async_client.setup_payment(
            customer_id="customer_id",
        )
        assert_matches_type(SetupPaymentResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_setup_payment_with_all_params(self, async_client: AsyncAutumn) -> None:
        client = await async_client.setup_payment(
            customer_id="customer_id",
            checkout_session_params={"foo": "bar"},
            customer_data={
                "disable_default": True,
                "email": "email",
                "fingerprint": "fingerprint",
                "metadata": {"foo": "bar"},
                "name": "name",
                "stripe_id": "stripe_id",
            },
            success_url="success_url",
        )
        assert_matches_type(SetupPaymentResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_setup_payment(self, async_client: AsyncAutumn) -> None:
        response = await async_client.with_raw_response.setup_payment(
            customer_id="customer_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(SetupPaymentResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_setup_payment(self, async_client: AsyncAutumn) -> None:
        async with async_client.with_streaming_response.setup_payment(
            customer_id="customer_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(SetupPaymentResponse, client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_track(self, async_client: AsyncAutumn) -> None:
        client = await async_client.track(
            customer_id="x",
        )
        assert_matches_type(TrackResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_track_with_all_params(self, async_client: AsyncAutumn) -> None:
        client = await async_client.track(
            customer_id="x",
            customer_data={
                "disable_default": True,
                "email": "email",
                "fingerprint": "fingerprint",
                "metadata": {"foo": "bar"},
                "name": "name",
                "stripe_id": "stripe_id",
            },
            entity_data={
                "feature_id": "feature_id",
                "name": "name",
            },
            entity_id="entity_id",
            event_name="x",
            feature_id="feature_id",
            idempotency_key="idempotency_key",
            overage_behavior="cap",
            properties={"foo": "bar"},
            skip_event=True,
            timestamp=0,
            value=0,
        )
        assert_matches_type(TrackResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_track(self, async_client: AsyncAutumn) -> None:
        response = await async_client.with_raw_response.track(
            customer_id="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(TrackResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_track(self, async_client: AsyncAutumn) -> None:
        async with async_client.with_streaming_response.track(
            customer_id="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(TrackResponse, client, path=["response"])

        assert cast(Any, response.is_closed) is True
