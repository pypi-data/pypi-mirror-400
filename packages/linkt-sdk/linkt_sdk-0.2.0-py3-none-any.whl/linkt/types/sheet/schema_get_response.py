# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["SchemaGetResponse"]


class SchemaGetResponse(BaseModel):
    """JSON schema for the sheet."""

    title: str
    """The title of the schema"""

    type: str
    """The type of the schema"""

    defs: Optional[Dict[str, object]] = FieldInfo(alias="$defs", default=None)
    """Definitions for nested schemas"""

    properties: Optional[Dict[str, object]] = None
    """The properties of the schema"""

    required: Optional[List[str]] = None
    """Required fields in the schema"""
