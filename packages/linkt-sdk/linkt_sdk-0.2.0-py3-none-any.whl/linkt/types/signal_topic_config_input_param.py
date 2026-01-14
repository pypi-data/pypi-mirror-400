# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

from .._types import SequenceNotStr
from .entity_type import EntityType
from .signal_type_config_param import SignalTypeConfigParam

__all__ = ["SignalTopicConfigInputParam"]


class SignalTopicConfigInputParam(TypedDict, total=False):
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

    signal_types: Required[Iterable[SignalTypeConfigParam]]
    """Types of signals to monitor for this topic"""

    topic_criteria: Required[str]
    """Natural language description of what to monitor"""

    company_size_filters: Optional[SequenceNotStr[str]]
    """Company size criteria (e.g., employee count ranges)"""

    config_type: Literal["signal-topic"]
    """Config type discriminator"""

    entity_type: EntityType
    """Type of entity being monitored (company, school district, person, etc.)"""

    geographic_filters: Optional[SequenceNotStr[str]]
    """Geographic regions to focus on"""

    industry_filters: Optional[SequenceNotStr[str]]
    """Industries to focus on"""

    monitoring_frequency: Literal["daily", "weekly", "monthly"]
    """How often to check for new signals (daily, weekly, monthly)"""

    version: Literal["v2.0"]
    """Config version"""

    webhook_url: Optional[str]
    """Optional webhook URL to notify when signal run completes"""
