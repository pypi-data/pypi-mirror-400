# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["SearchV3Config"]


class SearchV3Config(BaseModel):
    """Search v3.0 configuration with planning-driven approach.

    Key differences from v2.0:
    - No hardcoded discovery_prompt or analyst_prompt
    - desired_contact_count extracted from ICP builder session
    - user_feedback field for append-only feedback accumulation
    """

    config_type: Optional[Literal["search-task"]] = None
    """Normalized config type for all search tasks"""

    desired_contact_count: Optional[int] = None
    """Number of contacts to find per company (from ICP builder session)"""

    user_feedback: Optional[str] = None
    """Accumulated user feedback (append-only)"""

    version: Optional[Literal["v3.0"]] = None

    webhook_url: Optional[str] = None
    """Optional webhook URL to notify when workflow run completes"""
