# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

from .entity_target_config_param import EntityTargetConfigParam

__all__ = ["IcpCreateParams"]


class IcpCreateParams(TypedDict, total=False):
    description: Required[str]

    entity_targets: Required[Iterable[EntityTargetConfigParam]]

    name: Required[str]
