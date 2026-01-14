"""Validation schemas for data operations."""

from .base import JsonStr, NonEmptyStr
from .crawler import CrawlerToData


class InputToData(CrawlerToData):
    """
    Validation schema for data input operations.

    Note: No additional timestamp field required here.
    The ValidationHandler adds InputToData_validated_at when this class is validated.
    """


class DataToDatabase(InputToData):
    """Validation schema for data-to-database operations."""

    id: NonEmptyStr
    InputToData_validated_at: NonEmptyStr


class DataToCustomerDatabase(InputToData):
    """Validation schema for customer database output with JSON-serialized fields."""

    id: NonEmptyStr
    config_execution_row: JsonStr
    scraping_result: JsonStr
