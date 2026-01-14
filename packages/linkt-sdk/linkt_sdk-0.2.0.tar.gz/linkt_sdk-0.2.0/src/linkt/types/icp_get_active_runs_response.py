# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["IcpGetActiveRunsResponse", "Run"]


class Run(BaseModel):
    """Individual run status item for API responses.

    Includes both agent_type (execution context) and task_type (workflow type) fields
    to support filtering and display during the transition from legacy runs.

    Attributes:
        id: Unique run identifier (ObjectId as string)
        agent_type: HOW the run was triggered ("task", "play")
        task_type: WHAT workflow runs ("signal", "search", "profile", "ingest").
                   None for plays or legacy runs without this field.
        created_at: When the run was created
    """

    id: str
    """Run ID"""

    agent_type: str
    """Execution context (task, play)"""

    created_at: Optional[datetime] = None
    """Creation timestamp"""

    task_type: Optional[str] = None
    """Workflow type for task-based runs (signal, search, profile, ingest)"""


class IcpGetActiveRunsResponse(BaseModel):
    """Response model for ICP running status."""

    runs: List[Run]
