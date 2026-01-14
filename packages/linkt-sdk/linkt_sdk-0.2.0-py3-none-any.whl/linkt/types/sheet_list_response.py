# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List

from .._models import BaseModel

__all__ = ["SheetListResponse"]


class SheetListResponse(BaseModel):
    """Response model for sheet list."""

    page: int

    page_size: int

    sheets: List[Dict[str, object]]

    total: int
