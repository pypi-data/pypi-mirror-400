# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Optional
from typing_extensions import TypeAlias, TypedDict

from .search_v2_config_param import SearchV2ConfigParam
from .search_v3_config_param import SearchV3ConfigParam
from .ingest_task_config_param import IngestTaskConfigParam
from .standard_prompt_config_param import StandardPromptConfigParam
from .signal_csv_config_input_param import SignalCsvConfigInputParam
from .signal_sheet_config_input_param import SignalSheetConfigInputParam
from .signal_topic_config_input_param import SignalTopicConfigInputParam

__all__ = ["TaskUpdateParams", "TaskConfig"]


class TaskUpdateParams(TypedDict, total=False):
    deployment_name: Optional[str]
    """Updated deployment name"""

    description: Optional[str]
    """Updated task description"""

    icp_id: Optional[str]
    """Updated ICP Connection"""

    name: Optional[str]
    """Updated task name"""

    prompt: Optional[str]
    """Updated task prompt template"""

    task_config: Optional[TaskConfig]
    """Updated flow-specific task configuration with versioning"""


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
