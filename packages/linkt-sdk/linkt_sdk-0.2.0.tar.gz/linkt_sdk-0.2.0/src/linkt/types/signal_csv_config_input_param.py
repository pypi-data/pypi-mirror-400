# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

from .entity_type import EntityType
from .signal_type_config_param import SignalTypeConfigParam

__all__ = ["SignalCsvConfigInputParam"]


class SignalCsvConfigInputParam(TypedDict, total=False):
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

    file_id: Required[str]
    """ID of the uploaded CSV file"""

    signal_types: Required[Iterable[SignalTypeConfigParam]]
    """Types of signals to monitor for these entities"""

    config_type: Literal["signal-csv"]
    """Config type discriminator"""

    entity_type: EntityType
    """Type of entity being monitored (company, school district, person, etc.)"""

    monitoring_frequency: Literal["daily", "weekly", "monthly"]
    """How often to check for new signals (daily, weekly, monthly)"""

    primary_column: str
    """Column containing entity names.

    Defaults to 'name'. Used to extract entity names from CSV rows during signal
    workflow.
    """

    version: Literal["v2.0"]
    """Config version"""

    webhook_url: Optional[str]
    """Optional webhook URL to notify when signal run completes"""
