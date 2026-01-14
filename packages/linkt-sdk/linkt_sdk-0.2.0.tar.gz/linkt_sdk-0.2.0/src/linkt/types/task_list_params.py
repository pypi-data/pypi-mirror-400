# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["TaskListParams"]


class TaskListParams(TypedDict, total=False):
    flow_name: Optional[str]
    """Filter by flow name"""

    order: Optional[int]
    """Sort order: -1 for descending, 1 for ascending"""

    page: int
    """Page number (1-based)"""

    page_size: int
    """Items per page (max 100)"""

    sort_by: Optional[str]
    """Field to sort by (e.g., 'created_at', 'updated_at', 'name')"""
