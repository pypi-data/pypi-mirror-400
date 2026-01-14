# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["SearchV2ConfigParam"]


class SearchV2ConfigParam(TypedDict, total=False):
    """Search v2 dual-agent configuration."""

    analyst_prompt: Required[str]
    """Jinja2 analyst agent instructions"""

    discovery_prompt: Required[str]
    """Jinja2 discovery agent instructions"""

    config_type: Literal["search-prompt", "search-task"]
    """Config type (search-prompt for legacy, search-task for normalized)"""

    version: Literal["v2.0"]

    webhook_url: Optional[str]
    """Optional webhook URL to notify when workflow run completes"""
