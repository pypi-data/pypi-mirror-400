# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["EntityUpdateCommentsParams"]


class EntityUpdateCommentsParams(TypedDict, total=False):
    sheet_id: Required[str]

    comments: Optional[str]
    """Comments for the entity"""
