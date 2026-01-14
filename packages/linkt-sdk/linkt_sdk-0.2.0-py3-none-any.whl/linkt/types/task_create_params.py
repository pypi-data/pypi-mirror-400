# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Optional
from typing_extensions import Required, TypeAlias, TypedDict

from .search_v2_config_param import SearchV2ConfigParam
from .search_v3_config_param import SearchV3ConfigParam
from .ingest_task_config_param import IngestTaskConfigParam
from .standard_prompt_config_param import StandardPromptConfigParam
from .signal_csv_config_input_param import SignalCsvConfigInputParam
from .signal_sheet_config_input_param import SignalSheetConfigInputParam
from .signal_topic_config_input_param import SignalTopicConfigInputParam

__all__ = ["TaskCreateParams", "TaskConfig"]


class TaskCreateParams(TypedDict, total=False):
    deployment_name: Required[str]
    """The Prefect deployment name for this flow"""

    description: Required[str]
    """Detailed description of what this task accomplishes"""

    flow_name: Required[str]
    """The Prefect flow name (e.g., 'search', 'ingest', 'signal')"""

    name: Required[str]
    """Human-readable name for the task"""

    icp_id: Optional[str]
    """Optional ICP ID for signal monitoring tasks"""

    prompt: Optional[str]
    """Template prompt for the task. Can include placeholders for runtime parameters."""

    task_config: Optional[TaskConfig]
    """Flow-specific task configuration with versioning"""


TaskConfig: TypeAlias = Union[
    Dict[str, object],
    StandardPromptConfigParam,
    SearchV2ConfigParam,
    SearchV3ConfigParam,
    IngestTaskConfigParam,
    SignalTopicConfigInputParam,
    SignalCsvConfigInputParam,
    SignalSheetConfigInputParam,
]
