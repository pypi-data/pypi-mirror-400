# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, TypedDict

__all__ = ["IcpListParams"]


class IcpListParams(TypedDict, total=False):
    mode: Optional[Literal["discovery", "monitoring"]]
    """Filter by ICP mode: 'discovery' or 'monitoring'"""

    order: Optional[int]
    """Sort order: -1 for descending, 1 for ascending"""

    page: int

    page_size: int

    sort_by: Optional[str]
    """Field to sort by (e.g., 'created_at', 'updated_at', 'name')"""
