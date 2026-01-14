# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, TypedDict

__all__ = ["SearchV3ConfigParam"]


class SearchV3ConfigParam(TypedDict, total=False):
    """Search v3.0 configuration with planning-driven approach.

    Key differences from v2.0:
    - No hardcoded discovery_prompt or analyst_prompt
    - desired_contact_count extracted from ICP builder session
    - user_feedback field for append-only feedback accumulation
    """

    config_type: Literal["search-task"]
    """Normalized config type for all search tasks"""

    desired_contact_count: int
    """Number of contacts to find per company (from ICP builder session)"""

    user_feedback: str
    """Accumulated user feedback (append-only)"""

    version: Literal["v3.0"]

    webhook_url: Optional[str]
    """Optional webhook URL to notify when workflow run completes"""
