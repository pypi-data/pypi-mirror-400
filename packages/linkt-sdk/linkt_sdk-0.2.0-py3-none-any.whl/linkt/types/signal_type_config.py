# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["SignalTypeConfig"]


class SignalTypeConfig(BaseModel):
    """Configuration for a single signal type to monitor.

    Allows both standard signal types and custom types using OTHER.
    """

    description: str
    """Detailed description of what to monitor"""

    display: str
    """Display name for this signal type"""

    type: Literal[
        "funding",
        "leadership_change",
        "layoff",
        "product_launch",
        "partnership",
        "acquisition",
        "expansion",
        "award",
        "pivot",
        "regulatory",
        "rfp",
        "contract_renewal",
        "hiring_surge",
        "infrastructure",
        "compliance",
        "job_posting",
        "other",
    ]
    """Signal type to monitor (use OTHER for custom types)"""
