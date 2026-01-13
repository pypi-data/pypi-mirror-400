# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["AttachResponse"]


class AttachResponse(BaseModel):
    code: str

    customer_id: str

    message: str

    product_ids: List[str]

    success: bool

    checkout_url: Optional[str] = None

    invoice: Optional[object] = None
