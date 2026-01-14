# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

from .entity_type import EntityType
from .signal_type_config_param import SignalTypeConfigParam

__all__ = ["SignalSheetConfigInputParam"]


class SignalSheetConfigInputParam(TypedDict, total=False):
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

    signal_types: Required[Iterable[SignalTypeConfigParam]]
    """Types of signals to monitor"""

    source_icp_id: Required[str]
    """ID of the discovery ICP containing entities to monitor"""

    config_type: Literal["signal-sheet"]
    """Config type discriminator"""

    entity_filters: Optional[Dict[str, object]]
    """Optional MongoDB query to filter entities within the sheet"""

    entity_type: EntityType
    """Type of entity being monitored (company, person, school_district, etc.)"""

    monitoring_frequency: Literal["daily", "weekly", "monthly"]
    """How often to check for new signals"""

    version: Literal["v2.0"]
    """Config version"""

    webhook_url: Optional[str]
    """Optional webhook URL to notify when signal run completes"""
