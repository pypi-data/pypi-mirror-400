# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import TypedDict

__all__ = ["TaskExecuteParams"]


class TaskExecuteParams(TypedDict, total=False):
    icp_id: Optional[str]
    """Optional ICP ID to attach to this run for workflows that require ICP context"""

    parameters: Dict[str, object]
    """Runtime parameters to pass to the task execution"""
