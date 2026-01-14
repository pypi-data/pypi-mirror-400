# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["SearchV2Config"]


class SearchV2Config(BaseModel):
    """Search v2 dual-agent configuration."""

    analyst_prompt: str
    """Jinja2 analyst agent instructions"""

    discovery_prompt: str
    """Jinja2 discovery agent instructions"""

    config_type: Optional[Literal["search-prompt", "search-task"]] = None
    """Config type (search-prompt for legacy, search-task for normalized)"""

    version: Optional[Literal["v2.0"]] = None

    webhook_url: Optional[str] = None
    """Optional webhook URL to notify when workflow run completes"""
