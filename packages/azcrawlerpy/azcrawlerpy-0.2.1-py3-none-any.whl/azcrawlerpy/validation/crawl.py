"""Validation schemas for crawl operations."""

from .base import NonEmptyStr
from .config import ConfigToCrawl


class InputToCrawl(ConfigToCrawl):
    """
    Validation schema for crawl input data.

    Note: No additional timestamp field required here.
    The ValidationHandler adds InputToCrawl_validated_at when this class is validated.
    """


class CrawlToProxy(InputToCrawl):
    """Validation schema for crawl-to-proxy operations."""

    rule_proxy_account_name: NonEmptyStr
    strategy_proxy_fallback_account_name: NonEmptyStr
    rule_proxy_service_name: NonEmptyStr
    strategy_proxy_fallback_service_name: NonEmptyStr
    InputToCrawl_validated_at: NonEmptyStr
