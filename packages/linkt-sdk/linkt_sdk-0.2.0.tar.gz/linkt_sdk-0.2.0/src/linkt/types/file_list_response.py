# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .._models import BaseModel

__all__ = ["FileListResponse", "File"]


class File(BaseModel):
    """File item in list response."""

    file_id: str
    """The ID of the file"""

    name: str
    """The name of the file"""

    size_bytes: int
    """Size of the file in bytes"""


class FileListResponse(BaseModel):
    """Response model for file listing."""

    files: List[File]
    """List of files"""

    page: int
    """Current page number"""

    page_size: int
    """Number of items per page"""

    total: int
    """Total number of files"""
