# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from datetime import datetime
from typing_extensions import Literal, TypeAlias

from .._models import BaseModel
from .entity_type import EntityType
from .search_v2_config import SearchV2Config
from .search_v3_config import SearchV3Config
from .ingest_task_config import IngestTaskConfig
from .signal_type_config import SignalTypeConfig
from .standard_prompt_config import StandardPromptConfig

__all__ = [
    "TaskListResponse",
    "Task",
    "TaskTaskConfig",
    "TaskTaskConfigSignalTopicConfigOutput",
    "TaskTaskConfigSignalCsvConfigOutput",
    "TaskTaskConfigSignalSheetConfigOutput",
]


class TaskTaskConfigSignalTopicConfigOutput(BaseModel):
    """Topic-based signal monitoring configuration.

    Monitors signals based on criteria without requiring pre-existing entities.

    Attributes:
        version: Config version (always "v2.0")
        config_type: Config type discriminator (always "signal-topic")
        entity_type: Type of entity being monitored (company, person, etc.)
        topic_criteria: Natural language description of what to monitor
        signal_types: Types of signals to monitor for this topic
        monitoring_frequency: How often to check for signals (daily/weekly/monthly)
        geographic_filters: Optional geographic regions to focus on
        industry_filters: Optional industries to focus on
        company_size_filters: Optional company size criteria
        webhook_url: Optional webhook URL to notify when signal run completes
    """

    signal_types: List[SignalTypeConfig]
    """Types of signals to monitor for this topic"""

    topic_criteria: str
    """Natural language description of what to monitor"""

    company_size_filters: Optional[List[str]] = None
    """Company size criteria (e.g., employee count ranges)"""

    config_type: Optional[Literal["signal-topic"]] = None
    """Config type discriminator"""

    entity_type: Optional[EntityType] = None
    """Type of entity being monitored (company, school district, person, etc.)"""

    geographic_filters: Optional[List[str]] = None
    """Geographic regions to focus on"""

    industry_filters: Optional[List[str]] = None
    """Industries to focus on"""

    monitoring_frequency: Optional[Literal["daily", "weekly", "monthly"]] = None
    """How often to check for new signals (daily, weekly, monthly)"""

    version: Optional[Literal["v2.0"]] = None
    """Config version"""

    webhook_url: Optional[str] = None
    """Optional webhook URL to notify when signal run completes"""


class TaskTaskConfigSignalCsvConfigOutput(BaseModel):
    """CSV-based signal monitoring configuration.

    Monitors signals for companies/people uploaded via CSV file.

    Attributes:
        version: Config version (always "v2.0")
        config_type: Config type discriminator (always "signal-csv")
        entity_type: Type of entity being monitored (company, person, etc.)
        file_id: ID of the uploaded CSV file
        primary_column: Column containing entity names (defaults to "name")
        signal_types: Types of signals to monitor for these entities
        monitoring_frequency: How often to check for signals (daily/weekly/monthly)
        webhook_url: Optional webhook URL to notify when signal run completes
    """

    file_id: str
    """ID of the uploaded CSV file"""

    signal_types: List[SignalTypeConfig]
    """Types of signals to monitor for these entities"""

    config_type: Optional[Literal["signal-csv"]] = None
    """Config type discriminator"""

    entity_type: Optional[EntityType] = None
    """Type of entity being monitored (company, school district, person, etc.)"""

    monitoring_frequency: Optional[Literal["daily", "weekly", "monthly"]] = None
    """How often to check for new signals (daily, weekly, monthly)"""

    primary_column: Optional[str] = None
    """Column containing entity names.

    Defaults to 'name'. Used to extract entity names from CSV rows during signal
    workflow.
    """

    version: Optional[Literal["v2.0"]] = None
    """Config version"""

    webhook_url: Optional[str] = None
    """Optional webhook URL to notify when signal run completes"""


class TaskTaskConfigSignalSheetConfigOutput(BaseModel):
    """Sheet-based signal monitoring configuration.

    Monitors signals for entities from an existing discovery ICP's sheet.
    Unlike CSV mode, signals are deterministically linked to source entities
    without requiring analyst agent processing.

    UPDATED 2025-12-29: Removed source_sheet_id field.
    Sheets are uniquely identified by (source_icp_id, entity_type),
    so source_sheet_id was redundant and never used at runtime.

    Attributes:
        source_icp_id: ID of the discovery ICP containing entities to monitor
        entity_type: Type of entity being monitored (selects which sheet)
        entity_filters: Optional MongoDB query to filter entities
        signal_types: Types of signals to monitor
        monitoring_frequency: How often to check for signals
        webhook_url: Optional webhook URL to notify when signal run completes
    """

    signal_types: List[SignalTypeConfig]
    """Types of signals to monitor"""

    source_icp_id: str
    """ID of the discovery ICP containing entities to monitor"""

    config_type: Optional[Literal["signal-sheet"]] = None
    """Config type discriminator"""

    entity_filters: Optional[Dict[str, object]] = None
    """Optional MongoDB query to filter entities within the sheet"""

    entity_type: Optional[EntityType] = None
    """Type of entity being monitored (company, person, school_district, etc.)"""

    monitoring_frequency: Optional[Literal["daily", "weekly", "monthly"]] = None
    """How often to check for new signals"""

    version: Optional[Literal["v2.0"]] = None
    """Config version"""

    webhook_url: Optional[str] = None
    """Optional webhook URL to notify when signal run completes"""


TaskTaskConfig: TypeAlias = Union[
    Dict[str, object],
    StandardPromptConfig,
    SearchV2Config,
    SearchV3Config,
    IngestTaskConfig,
    TaskTaskConfigSignalTopicConfigOutput,
    TaskTaskConfigSignalCsvConfigOutput,
    TaskTaskConfigSignalSheetConfigOutput,
    None,
]


class Task(BaseModel):
    """Response model for task data."""

    id: str
    """Task ID"""

    created_at: datetime
    """Creation timestamp"""

    deployment_name: str
    """Prefect deployment name"""

    description: str
    """Task description"""

    flow_name: str
    """Prefect flow name"""

    name: str
    """Task name"""

    updated_at: datetime
    """Last update timestamp"""

    icp_id: Optional[str] = None
    """Task ICP ID"""

    prompt: Optional[str] = None
    """Template prompt for the task. Can include placeholders for runtime parameters."""

    task_config: Optional[TaskTaskConfig] = None
    """Flow-specific task configuration with versioning"""


class TaskListResponse(BaseModel):
    """Response model for paginated task list."""

    page: int
    """Current page number (1-based)"""

    page_size: int
    """Number of items per page"""

    tasks: List[Task]
    """List of tasks"""

    total: int
    """Total number of tasks matching filters"""
