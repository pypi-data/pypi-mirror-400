# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from datetime import datetime

from .._models import BaseModel

__all__ = ["IcpResponse", "EntityTarget"]


class EntityTarget(BaseModel):
    """Response model for entity target configuration."""

    description: str

    entity_type: str

    root: bool


class IcpResponse(BaseModel):
    """Response model for ICP."""

    id: str

    created_at: datetime

    description: str

    entity_targets: List[EntityTarget]

    name: str

    updated_at: datetime
