"""Validation schemas for crawler operations."""

from .base import NonEmptyDict, NonEmptyStr
from .proxy import ProxyToCrawler


class InputToCrawler(ProxyToCrawler):
    """
    Validation schema for crawler input data.

    Note: No additional timestamp field required here.
    The ValidationHandler adds InputToCrawler_validated_at when this class is validated.
    """


class CrawlerToData(InputToCrawler):
    """Validation schema for crawler-to-data operations."""

    scraping_result: NonEmptyDict
    InputToCrawler_validated_at: NonEmptyStr
