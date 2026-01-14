# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List

from .._models import BaseModel

__all__ = ["SheetGetEntitiesResponse"]


class SheetGetEntitiesResponse(BaseModel):
    """Response schema for paginated list of sheet entities.

    Uses EntityForHTTP which automatically excludes embedding data
    for efficient API responses.

    Attributes:
        entities: List of EntityForHTTP objects for the current page
        total: Total number of entities matching the filter criteria
        page: Current page number (1-based)
        page_size: Number of items per page
    """

    entities: List[Dict[str, object]]

    page: int

    page_size: int

    total: int
