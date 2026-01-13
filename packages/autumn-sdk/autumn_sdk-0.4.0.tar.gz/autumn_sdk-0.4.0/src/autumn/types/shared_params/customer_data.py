# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import TypedDict

__all__ = ["CustomerData"]


class CustomerData(TypedDict, total=False):
    """Customer details to set when creating a customer"""

    disable_default: bool

    email: Optional[str]
    """Customer's email address"""

    fingerprint: Optional[str]

    metadata: Optional[Dict[str, object]]

    name: Optional[str]
    """Customer's name"""

    stripe_id: Optional[str]
