# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["IngestTaskConfig"]


class IngestTaskConfig(BaseModel):
    """Configuration for one-time CSV enrichment tasks.

    Used by ingest_csv workflows to enrich entities from uploaded CSV files.
    The csv_entity_type tracks the entity type of rows IN THE CSV, which may
    differ from the ICP hierarchy (e.g., CSV has people, but ICP has company→person).

    Attributes:
        file_id: Reference to uploaded CSV file in S3 (via File document)
        primary_column: Column containing entity names for matching
        csv_entity_type: Entity type of rows in CSV (may differ from ICP hierarchy)
    """

    csv_entity_type: str
    """Entity type in the CSV (e.g., 'person', 'company')"""

    file_id: str
    """File ID referencing uploaded CSV in MongoDB"""

    primary_column: str
    """Column containing entity names"""

    config_type: Optional[Literal["ingest-task"]] = None
    """Config type for ingest tasks"""

    version: Optional[Literal["v1.0"]] = None

    webhook_url: Optional[str] = None
    """Optional webhook URL to notify when workflow run completes"""
