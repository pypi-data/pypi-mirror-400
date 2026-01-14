"""Validation schemas for crawler input data."""

from .base import Base, JsonStr, NonEmptyDict, NonEmptyStr
from .config import ConfigToCrawl, InputToConfig
from .crawl import CrawlToProxy, InputToCrawl
from .crawler import CrawlerToData, InputToCrawler
from .data import DataToCustomerDatabase, DataToDatabase, InputToData
from .proxy import InputToProxy, ProxyToCrawler
from .request import InputToRequest, RequestToConfig

__all__ = [
    "Base",
    "ConfigToCrawl",
    "CrawlToProxy",
    "CrawlerToData",
    "DataToCustomerDatabase",
    "DataToDatabase",
    "InputToConfig",
    "InputToCrawl",
    "InputToCrawler",
    "InputToData",
    "InputToProxy",
    "InputToRequest",
    "JsonStr",
    "NonEmptyDict",
    "NonEmptyStr",
    "ProxyToCrawler",
    "RequestToConfig",
]
