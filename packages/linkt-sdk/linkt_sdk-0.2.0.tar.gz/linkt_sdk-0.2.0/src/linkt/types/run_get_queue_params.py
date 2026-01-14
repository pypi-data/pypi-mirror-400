# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["RunGetQueueParams"]


class RunGetQueueParams(TypedDict, total=False):
    include_history: bool
    """Include processing history from all states"""

    limit: int
    """Maximum number of entities to return"""

    offset: int
    """Starting position in queue (0-indexed)"""

    state: Optional[str]
    """Filter by state: queued, processing, completed, discarded"""
