# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .entity_type import EntityType

__all__ = ["SheetCreateParams"]


class SheetCreateParams(TypedDict, total=False):
    description: Required[str]

    entity_type: Required[EntityType]
    """Type of entities to store"""

    icp_id: Required[str]
    """ICP this sheet belongs to"""

    name: Required[str]
