# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["SignalListParams"]


class SignalListParams(TypedDict, total=False):
    days: int
    """Number of days to look back"""

    entity_id: Optional[str]
    """Filter by entity"""

    icp_id: Optional[str]
    """Filter by ICP"""

    order: Optional[int]
    """Sort order: -1 for descending, 1 for ascending"""

    page: int

    page_size: int

    search_term: Optional[str]
    """Search in signal summary or type"""

    signal_type: Optional[str]
    """Filter by type"""

    sort_by: Optional[str]
    """Field to sort by (e.g., 'created_at', 'updated_at', 'signal_type', 'strength')"""

    strength: Optional[str]
    """Filter by strength"""
