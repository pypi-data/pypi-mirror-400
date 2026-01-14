"""Validation schemas for config operations."""

from .base import NonEmptyDict, NonEmptyStr
from .request import RequestToConfig


class InputToConfig(RequestToConfig):
    """
    Validation schema for config input data.

    Note: No additional fields required here.
    Inherits all fields from RequestToConfig (and transitively InputToRequest).
    The ValidationHandler adds InputToConfig_validated_at when this class is validated.
    """


class ConfigToCrawl(InputToConfig):
    """Validation schema for config-to-crawl operations."""

    config_source: NonEmptyStr
    compute_target: NonEmptyStr
    data_target: NonEmptyStr
    subscriber: NonEmptyStr
    InputToConfig_validated_at: NonEmptyStr
    config_execution_row: NonEmptyDict
