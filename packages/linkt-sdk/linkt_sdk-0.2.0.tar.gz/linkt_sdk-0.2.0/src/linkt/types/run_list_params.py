# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from datetime import datetime
from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["RunListParams"]


class RunListParams(TypedDict, total=False):
    agent_id: Optional[str]
    """Filter by agent ID (legacy)"""

    agent_type: Optional[str]
    """Filter by agent type"""

    created_after: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter runs created after this date (ISO 8601 format: 2024-01-15T10:30:00Z)"""

    created_before: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter runs created before this date (ISO 8601 format)"""

    icp_id: Optional[str]
    """Filter by ICP ID"""

    order: Optional[int]
    """Sort order: -1 for descending, 1 for ascending"""

    page: int
    """Page number (1-based)"""

    page_size: int
    """Items per page (max 100)"""

    sort_by: Optional[str]
    """Field to sort by (e.g., 'created_at', 'updated_at', 'agent_type')"""

    status: Optional[Literal["SCHEDULED", "PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELED", "CRASHED", "PAUSED"]]
    """
    Filter by run status (SCHEDULED, PENDING, RUNNING, COMPLETED, FAILED, CANCELED,
    CRASHED, PAUSED)
    """

    task_id: Optional[str]
    """Filter by task ID"""

    task_type: Optional[str]
    """Filter by task type (signal, search, profile, ingest)"""

    updated_after: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter runs updated after this date (ISO 8601 format)"""

    updated_before: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """Filter runs updated before this date (ISO 8601 format)"""
