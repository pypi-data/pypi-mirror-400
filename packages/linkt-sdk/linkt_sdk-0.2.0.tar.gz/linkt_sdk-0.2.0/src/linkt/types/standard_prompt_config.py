# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["StandardPromptConfig"]


class StandardPromptConfig(BaseModel):
    """
    Standard single-prompt configuration for most flows.
    Used by: ingest, profile, signal, and future single-prompt flows.

    NOTE: config_type should match flow_name (e.g., 'profile-prompt', 'ingest-prompt').
    This is enforced by Task model validator.
    """

    config_type: str
    """Config type (e.g., 'profile-prompt', 'ingest-prompt')"""

    prompt: str
    """Jinja2 template for task instructions"""

    version: Optional[Literal["v1.0"]] = None

    webhook_url: Optional[str] = None
    """Optional webhook URL to notify when workflow run completes"""
