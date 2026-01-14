# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from datetime import datetime
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["SheetGetEntitiesParams"]


class SheetGetEntitiesParams(TypedDict, total=False):
    created_after: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter entities created after this date (ISO 8601 format: 2024-01-15T10:30:00Z)"""

    created_before: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter entities created before this date (ISO 8601 format)"""

    has_comments: Optional[bool]
    """Filter entities with or without user comments"""

    order: Optional[int]
    """Sort order: -1 for descending, 1 for ascending"""

    page: int
    """Page number (1-based)"""

    page_size: int
    """Items per page (max 100, default 50)"""

    search: Optional[str]
    """Search entities by name or company"""

    sort_by: Optional[str]
    """Field to sort by (e.g., 'created_at', 'updated_at', 'status')"""

    status: Optional[bool]
    """Filter by entity status (true=active, false=inactive)"""

    updated_after: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter entities updated after this date (ISO 8601 format)"""

    updated_before: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter entities updated before this date (ISO 8601 format)"""
