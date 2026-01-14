"""
Utility functions for the crawler framework.

Date formatting, selector utilities, and other helper functions.
"""

import logging
from datetime import datetime
from typing import Any

from .config import CSS_ATTRIBUTE_VALUE_ESCAPE_CHARS, CSS_SELECTOR_ESCAPE_CHARS
from .exceptions import InvalidInstructionError


def setup_logger(name: str) -> logging.Logger:
    """Create a structured logger for the crawler framework."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def format_date(value: str, target_format: str) -> str:
    """
    Convert a date string to the target format.

    Input format is expected to be ISO 8601 (YYYY-MM-DD).
    Target format uses strftime directives mapped from common patterns.

    Args:
        value: Date string in ISO 8601 format (YYYY-MM-DD)
        target_format: Target format pattern (e.g., "DD.MM.YYYY", "MM/DD/YYYY")

    Returns:
        Formatted date string

    """
    # Using naive datetime intentionally - we're only converting date formats, not handling timezones
    input_date = datetime.strptime(value, "%Y-%m-%d")  # noqa: DTZ007

    format_mapping: dict[str, str] = {
        "DD.MM.YYYY": "%d.%m.%Y",
        "MM/DD/YYYY": "%m/%d/%Y",
        "YYYY-MM-DD": "%Y-%m-%d",
        "DD/MM/YYYY": "%d/%m/%Y",
        "YYYY/MM/DD": "%Y/%m/%d",
        "DD-MM-YYYY": "%d-%m-%Y",
        "MM-DD-YYYY": "%m-%d-%Y",
    }

    strftime_format = format_mapping.get(target_format)
    if strftime_format is None:
        msg = f"Unsupported date format: {target_format}"
        raise InvalidInstructionError(msg)

    return input_date.strftime(strftime_format)


def get_value_for_field(input_data: dict[str, Any], data_key: str) -> Any:
    """
    Retrieve a value from input_data by key.

    Does not provide defaults - missing keys will be handled by the caller
    through MissingDataError.

    Args:
        input_data: Dictionary of field values
        data_key: Key to retrieve

    Returns:
        The value if found, or None if key does not exist

    """
    return input_data.get(data_key)


def normalize_selector(selector: str) -> str:
    """
    Normalize a CSS selector for consistent usage.

    Strips whitespace and validates basic selector syntax.

    Args:
        selector: CSS selector string

    Returns:
        Normalized selector string

    """
    normalized = selector.strip()
    if not normalized:
        msg = "Empty selector provided"
        raise InvalidInstructionError(msg)
    return normalized


def escape_css_id(element_id: str) -> str:
    """
    Escape special characters in CSS ID selectors.

    Characters like :, [], (), etc. need backslash escaping.

    Args:
        element_id: Raw element ID

    Returns:
        Escaped ID safe for use in CSS selectors

    """
    escaped = ""
    for char in element_id:
        if char in CSS_SELECTOR_ESCAPE_CHARS:
            escaped += "\\" + char
        else:
            escaped += char
    return escaped


def escape_css_attribute_value(value: str) -> str:
    """
    Escape special characters in CSS attribute selector values.

    Handles quotes, backslashes, and bracket characters that could break
    attribute selectors like [data-cy='value'].

    Args:
        value: Raw value to use in attribute selector

    Returns:
        Escaped value safe for use in CSS attribute selectors

    """
    escaped = ""
    for char in value:
        if char in CSS_ATTRIBUTE_VALUE_ESCAPE_CHARS:
            escaped += "\\" + char
        else:
            escaped += char
    return escaped


def interpolate_selector_value(selector: str, value: str) -> str:
    """
    Safely interpolate a value into a selector placeholder.

    Replaces ${value} placeholder with an escaped version of the value.

    Args:
        selector: Selector template containing ${value} placeholder
        value: Value to interpolate

    Returns:
        Selector with value safely interpolated

    """
    escaped_value = escape_css_attribute_value(str(value))
    return selector.replace("${value}", escaped_value)


def validate_css_selector_syntax(selector: str) -> bool:
    """
    Perform basic CSS selector syntax validation.

    Checks for balanced brackets and quotes.

    Args:
        selector: CSS selector to validate

    Returns:
        True if selector appears syntactically valid

    """
    bracket_pairs = {"[": "]", "(": ")"}
    stack: list[str] = []
    in_quote: str | None = None

    for char in selector:
        if in_quote:
            if char == in_quote:
                in_quote = None
        elif char in "\"'":
            in_quote = char
        elif char in bracket_pairs:
            stack.append(bracket_pairs[char])
        elif char in bracket_pairs.values():
            if not stack or stack.pop() != char:
                return False

    return len(stack) == 0 and in_quote is None
