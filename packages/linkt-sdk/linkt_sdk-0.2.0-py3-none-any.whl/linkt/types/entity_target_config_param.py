# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .._types import SequenceNotStr

__all__ = ["EntityTargetConfigParam"]


class EntityTargetConfigParam(TypedDict, total=False):
    """Request model for entity target configuration."""

    description: Required[str]
    """Business description of targets"""

    entity_type: Required[str]
    """Entity type to target"""

    filters: SequenceNotStr[str]
    """Filters to apply"""
