# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, TypedDict

from .shared_params.customer_data import CustomerData

__all__ = ["ClientSetupPaymentParams"]


class ClientSetupPaymentParams(TypedDict, total=False):
    customer_id: Required[str]
    """The ID of the customer"""

    checkout_session_params: Dict[str, object]
    """Additional parameters for the checkout session"""

    customer_data: CustomerData
    """Customer details to set when creating a customer"""

    success_url: str
    """URL to redirect to after successful payment setup.

    Must start with either http:// or https://
    """
