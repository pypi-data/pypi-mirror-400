"""Validation schemas for proxy operations."""

from .base import NonEmptyDict, NonEmptyStr
from .crawl import CrawlToProxy


class InputToProxy(CrawlToProxy):
    """
    Validation schema for proxy input data.

    Note: No additional timestamp field required here.
    The ValidationHandler adds InputToProxy_validated_at when this class is validated.
    """


class ProxyToCrawler(InputToProxy):
    """Validation schema for proxy-to-crawler operations."""

    set_proxy_account: NonEmptyDict
    InputToProxy_validated_at: NonEmptyStr
