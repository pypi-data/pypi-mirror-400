# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime

from ..._models import BaseModel

__all__ = ["Sheet"]


class Sheet(BaseModel):
    """Response model for sheet."""

    id: str

    created_at: datetime

    description: str

    entity_schema: Dict[str, object]

    icp_id: str

    name: str

    updated_at: datetime

    entity_type: Optional[str] = None
