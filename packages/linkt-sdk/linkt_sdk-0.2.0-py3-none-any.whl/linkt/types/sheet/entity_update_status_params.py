# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["EntityUpdateStatusParams"]


class EntityUpdateStatusParams(TypedDict, total=False):
    sheet_id: Required[str]

    status: Required[bool]
