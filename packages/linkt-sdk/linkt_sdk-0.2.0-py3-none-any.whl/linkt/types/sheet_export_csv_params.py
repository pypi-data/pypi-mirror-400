# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

from .._types import SequenceNotStr

__all__ = ["SheetExportCsvParams"]


class SheetExportCsvParams(TypedDict, total=False):
    entity_ids: Optional[SequenceNotStr[str]]
    """Optional list of entity IDs to export. If not provided, exports all entities."""
