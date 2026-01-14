# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List

from .._models import BaseModel

__all__ = ["RunListResponse"]


class RunListResponse(BaseModel):
    """Response schema for paginated list of agent runs.

    Follows the established pattern from other list endpoints:
    - SheetListResponse (src/api/schema/sheet.py)
    - ICPListResponse (src/api/schema/icp.py)

    Attributes:
        runs: List of AgentRun objects for the current page
        total: Total number of runs matching the filter criteria
        page: Current page number (1-based)
        page_size: Number of items per page
    """

    page: int

    page_size: int

    runs: List[Dict[str, object]]

    total: int
