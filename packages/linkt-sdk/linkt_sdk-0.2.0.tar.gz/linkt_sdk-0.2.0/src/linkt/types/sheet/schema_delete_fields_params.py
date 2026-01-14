# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ..._types import SequenceNotStr

__all__ = ["SchemaDeleteFieldsParams"]


class SchemaDeleteFieldsParams(TypedDict, total=False):
    fields: Required[SequenceNotStr[str]]
