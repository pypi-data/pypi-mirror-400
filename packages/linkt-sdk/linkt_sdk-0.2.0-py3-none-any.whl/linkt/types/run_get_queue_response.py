# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from .._models import BaseModel

__all__ = ["RunGetQueueResponse"]


class RunGetQueueResponse(BaseModel):
    """Response schema for run queue status with optional history.

    Provides a read-only view into the current state of a run's entity queue,
    including queued entities, processing history, and statistics.

    Attributes:
        entities: List of entities (current queue or full history based on request)
        stats: Queue statistics or state counts
        total: Total number of entities returned
        offset: Offset used for pagination (0-indexed)
        limit: Maximum number of entities returned
        state_counts: Optional breakdown of entities by state
        include_history: Whether response includes historical data
    """

    entities: List[Dict[str, object]]

    limit: int

    offset: int

    stats: Dict[str, object]

    total: int

    include_history: Optional[bool] = None

    state_counts: Optional[Dict[str, int]] = None
