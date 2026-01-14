# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel
from .signal_response import SignalResponse

__all__ = ["SignalListResponse"]


class SignalListResponse(BaseModel):
    """Response for listing signals."""

    page: int

    page_size: int

    signals: List[SignalResponse]

    total: int
