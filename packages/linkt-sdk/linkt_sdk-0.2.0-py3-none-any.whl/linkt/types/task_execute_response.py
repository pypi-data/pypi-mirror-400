# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["TaskExecuteResponse"]


class TaskExecuteResponse(BaseModel):
    """Response model for task execution."""

    flow_run_id: str
    """The Prefect flow run ID"""

    run_id: str
    """The ID of the created run"""

    status: str
    """Initial status of the run"""
