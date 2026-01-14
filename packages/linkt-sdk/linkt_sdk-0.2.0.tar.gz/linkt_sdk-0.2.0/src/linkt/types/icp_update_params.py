# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import TypedDict

from .entity_target_config_param import EntityTargetConfigParam

__all__ = ["IcpUpdateParams"]


class IcpUpdateParams(TypedDict, total=False):
    description: Optional[str]

    entity_targets: Optional[Iterable[EntityTargetConfigParam]]

    name: Optional[str]
