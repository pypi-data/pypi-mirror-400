# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel
from .icp_response import IcpResponse

__all__ = ["IcpListResponse"]


class IcpListResponse(BaseModel):
    """Response for listing ICPs."""

    icps: List[IcpResponse]

    page: int

    page_size: int

    total: int
