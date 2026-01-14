# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["SignalResponse"]


class SignalResponse(BaseModel):
    """Response model for signals (read-only)."""

    id: str

    created_at: datetime

    entity_ids: List[str]

    icp_id: str

    references: List[str]

    signal_type: Optional[str] = None

    strength: Optional[str] = None

    summary: str
