# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["IngestTaskConfigParam"]


class IngestTaskConfigParam(TypedDict, total=False):
    """Configuration for one-time CSV enrichment tasks.

    Used by ingest_csv workflows to enrich entities from uploaded CSV files.
    The csv_entity_type tracks the entity type of rows IN THE CSV, which may
    differ from the ICP hierarchy (e.g., CSV has people, but ICP has company→person).

    Attributes:
        file_id: Reference to uploaded CSV file in S3 (via File document)
        primary_column: Column containing entity names for matching
        csv_entity_type: Entity type of rows in CSV (may differ from ICP hierarchy)
    """

    csv_entity_type: Required[str]
    """Entity type in the CSV (e.g., 'person', 'company')"""

    file_id: Required[str]
    """File ID referencing uploaded CSV in MongoDB"""

    primary_column: Required[str]
    """Column containing entity names"""

    config_type: Literal["ingest-task"]
    """Config type for ingest tasks"""

    version: Literal["v1.0"]

    webhook_url: Optional[str]
    """Optional webhook URL to notify when workflow run completes"""
