# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional

from .._models import BaseModel
from .csv_processing_status import CsvProcessingStatus

__all__ = ["FileRetrieveResponse"]


class FileRetrieveResponse(BaseModel):
    """Response model for file details."""

    content_type: str
    """Content type of the file"""

    file_id: str
    """The ID of the file"""

    name: str
    """The name of the file"""

    s3_uri: str
    """S3 URI of the file"""

    size_bytes: int
    """Size of the file in bytes"""

    csv_metadata: Optional[Dict[str, object]] = None
    """CSV metadata"""

    original_file_type: Optional[str] = None
    """Original file type if converted (e.g., 'xlsx' if XLSX was converted to CSV)"""

    processing_status: Optional[CsvProcessingStatus] = None
    """Processing status"""
