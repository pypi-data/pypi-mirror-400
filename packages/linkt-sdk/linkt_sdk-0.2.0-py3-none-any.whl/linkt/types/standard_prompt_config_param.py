# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["StandardPromptConfigParam"]


class StandardPromptConfigParam(TypedDict, total=False):
    """
    Standard single-prompt configuration for most flows.
    Used by: ingest, profile, signal, and future single-prompt flows.

    NOTE: config_type should match flow_name (e.g., 'profile-prompt', 'ingest-prompt').
    This is enforced by Task model validator.
    """

    config_type: Required[str]
    """Config type (e.g., 'profile-prompt', 'ingest-prompt')"""

    prompt: Required[str]
    """Jinja2 template for task instructions"""

    version: Literal["v1.0"]

    webhook_url: Optional[str]
    """Optional webhook URL to notify when workflow run completes"""
