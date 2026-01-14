# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Required, TypedDict

__all__ = ["RunCreateParams"]


class RunCreateParams(TypedDict, total=False):
    agent_id: Required[str]

    parameters: Required[Dict[str, object]]

    icp_id: Optional[str]
