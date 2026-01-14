# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["SchemaAddFieldsParams", "Field"]


class SchemaAddFieldsParams(TypedDict, total=False):
    fields: Required[Iterable[Field]]


class Field(TypedDict, total=False):
    """Definition for a custom field in a sheet."""

    field_type: Required[Literal["string", "number", "integer", "boolean", "array", "object", "reference", "enum"]]
    """Field type"""

    name: Required[str]
    """Field name"""

    additional_props: Dict[str, object]
    """Additional JSON schema properties"""

    array_items: Optional[Dict[str, object]]
    """Schema for array items when field_type is ARRAY"""

    description: str
    """Field description"""

    enum_values: Optional[Iterable[object]]
    """List of allowed values when field_type is ENUM"""

    properties: Optional[Dict[str, object]]
    """Properties for object fields when field_type is OBJECT"""

    reference_model: Optional[str]
    """Referenced model name when field_type is REFERENCE"""

    required: bool
    """Whether field is required - always false for custom fields"""
