"""Crawling module for navigating and filling multi-step web forms."""

from .browser_utils import handle_cookie_consent
from .config import DEFAULT_USER_AGENT
from .crawler import FormCrawler
from .data_extraction import extract_data, extract_field_value
from .discovery import ElementDiscovery
from .discovery_models import (
    DiscoveredElement,
    ElementVisibility,
    IframeDiscovery,
    PageDiscoveryReport,
    RadioButtonGroup,
)
from .exceptions import (
    CrawlerError,
    CrawlerTimeoutError,
    DataExtractionError,
    FieldInteractionError,
    FieldNotFoundError,
    IframeNotFoundError,
    InvalidInstructionError,
    MissingDataError,
    NavigationError,
    UnsupportedActionTypeError,
    UnsupportedFieldTypeError,
)
from .models import (
    ActionDefinition,
    ActionType,
    CrawlResult,
    DataExtractionConfig,
    DebugMode,
    ExtractionFieldDefinition,
    FieldDefinition,
    FieldType,
    FinalPageDefinition,
    InMemoryCrawlResult,
    Instructions,
    StepDefinition,
    StepExtractionDefinition,
)

__all__ = [
    "DEFAULT_USER_AGENT",
    "ActionDefinition",
    "ActionType",
    "CrawlResult",
    "CrawlerError",
    "CrawlerTimeoutError",
    "DataExtractionConfig",
    "DataExtractionError",
    "DebugMode",
    "DiscoveredElement",
    "ElementDiscovery",
    "ElementVisibility",
    "ExtractionFieldDefinition",
    "FieldDefinition",
    "FieldInteractionError",
    "FieldNotFoundError",
    "FieldType",
    "FinalPageDefinition",
    "FormCrawler",
    "IframeDiscovery",
    "IframeNotFoundError",
    "InMemoryCrawlResult",
    "Instructions",
    "InvalidInstructionError",
    "MissingDataError",
    "NavigationError",
    "PageDiscoveryReport",
    "RadioButtonGroup",
    "StepDefinition",
    "StepExtractionDefinition",
    "UnsupportedActionTypeError",
    "UnsupportedFieldTypeError",
    "extract_data",
    "extract_field_value",
    "handle_cookie_consent",
]
