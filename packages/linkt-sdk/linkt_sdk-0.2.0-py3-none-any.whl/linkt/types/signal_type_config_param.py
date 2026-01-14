# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["SignalTypeConfigParam"]


class SignalTypeConfigParam(TypedDict, total=False):
    """Configuration for a single signal type to monitor.

    Allows both standard signal types and custom types using OTHER.
    """

    description: Required[str]
    """Detailed description of what to monitor"""

    display: Required[str]
    """Display name for this signal type"""

    type: Required[
        Literal[
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
    ]
    """Signal type to monitor (use OTHER for custom types)"""
