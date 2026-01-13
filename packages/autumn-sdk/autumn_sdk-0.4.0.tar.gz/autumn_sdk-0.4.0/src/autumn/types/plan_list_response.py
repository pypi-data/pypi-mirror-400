# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel
from .shared.plan import Plan

__all__ = ["PlanListResponse"]


class PlanListResponse(BaseModel):
    list: List[Plan]
