"""
Data extraction utilities for extracting structured data from HTML pages.

This module provides functions to extract data from the final page using
CSS selectors, element attributes, and optional regex patterns.
"""

import re
from typing import Any

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import FrameLocator, Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from .exceptions import DataExtractionError
from .models import (
    DataExtractionConfig,
    ExtractionFieldDefinition,
    NestedFieldDefinition,
    NestedOutputFormat,
)
from .utils import setup_logger

logger = setup_logger(__name__)


def _build_nested_fields(
    flat_data: dict[str, Any],
    nested_config: dict[str, NestedFieldDefinition],
) -> dict[str, Any]:
    """
    Build nested field structures from flat extracted data.

    Args:
        flat_data: Dictionary of flat extracted fields
        nested_config: Nested field configuration

    Returns:
        Dictionary mapping nested field names to structured values

    """
    result: dict[str, Any] = {}

    for output_name, config in nested_config.items():
        if config.output_format == NestedOutputFormat.PAIRED_DICT:
            keys = flat_data.get(config.key_field, [])
            values = flat_data.get(config.value_field, [])
            if not isinstance(keys, list):
                keys = [keys] if keys is not None else []
            if not isinstance(values, list):
                values = [values] if values is not None else []
            result[output_name] = dict(zip(keys, values, strict=False))
            logger.info(
                f"Built nested field: name='{output_name}' format='paired_dict' "
                f"keys={len(keys)} values={len(values)}"
            )

        elif config.output_format == NestedOutputFormat.OBJECT_LIST:
            source_arrays: dict[str, list[Any]] = {}
            for target_key, source_field in (config.fields or {}).items():
                source_value = flat_data.get(source_field, [])
                if not isinstance(source_value, list):
                    source_value = [source_value] if source_value is not None else []
                source_arrays[target_key] = source_value

            if source_arrays:
                length = max(len(arr) for arr in source_arrays.values())
                result[output_name] = [
                    {
                        key: arr[i] if i < len(arr) else None
                        for key, arr in source_arrays.items()
                    }
                    for i in range(length)
                ]
            else:
                result[output_name] = []

            logger.info(
                f"Built nested field: name='{output_name}' format='object_list' "
                f"items={len(result[output_name])}"
            )

    return result


def _apply_regex(value: str | None, pattern: str | None) -> str | None:
    """
    Apply regex pattern to extracted value if provided.

    Args:
        value: Raw extracted string value
        pattern: Regex pattern with optional capture group

    Returns:
        First capture group or full match if pattern provided, stripped value otherwise

    """
    if value is None:
        return None
    if pattern is None:
        return value.strip()

    match = re.search(pattern=pattern, string=value)
    if match is None:
        return None

    if match.groups():
        return match.group(1)
    return match.group(0)


async def extract_field_value(
    page: Page,
    field_name: str,
    field_def: ExtractionFieldDefinition,
) -> str | list[str] | None:
    """
    Extract a single field value from the page.

    Args:
        page: Playwright page instance
        field_name: Name of the field being extracted (for error context)
        field_def: Extraction field definition

    Returns:
        Extracted value(s) - string for single match, list for multiple matches,
        None if no matches found and multiple=False

    """
    try:
        context: Page | FrameLocator = (
            page.frame_locator(selector=field_def.iframe_selector)
            if field_def.iframe_selector is not None
            else page
        )
        locator = context.locator(field_def.selector)
        count = await locator.count()

        if count == 0:
            if field_def.multiple:
                return []
            return None

        if field_def.multiple:
            raw_values: list[str] = []
            for i in range(count):
                element = locator.nth(index=i)
                raw_value = (
                    await element.get_attribute(name=field_def.attribute)
                    if field_def.attribute
                    else await element.text_content()
                )
                if raw_value is not None:
                    processed = _apply_regex(value=raw_value, pattern=field_def.regex)
                    if processed is not None:
                        raw_values.append(processed)
            return raw_values

        element = locator.first
        raw_value = (
            await element.get_attribute(name=field_def.attribute)
            if field_def.attribute
            else await element.text_content()
        )
        if raw_value is None:
            return None
        return _apply_regex(value=raw_value, pattern=field_def.regex)

    except (PlaywrightTimeoutError, PlaywrightError) as e:
        raise DataExtractionError(
            field_name=field_name,
            selector=field_def.selector,
            reason=str(e),
        ) from e


async def extract_data(
    page: Page,
    config: DataExtractionConfig,
) -> dict[str, Any]:
    """
    Extract all configured data fields from the page.

    Args:
        page: Playwright page instance
        config: Data extraction configuration

    Returns:
        Dictionary mapping field names to extracted values

    """
    extracted: dict[str, Any] = {}

    for field_name, field_def in config.fields.items():
        value = await extract_field_value(
            page=page,
            field_name=field_name,
            field_def=field_def,
        )
        extracted[field_name] = value
        result_count = len(value) if isinstance(value, list) else (0 if value is None else 1)
        logger.info(
            f"Extracted field: name='{field_name}' selector='{field_def.selector}' "
            f"multiple={field_def.multiple} result_count={result_count}"
        )

    if config.nested_fields:
        nested_data = _build_nested_fields(
            flat_data=extracted,
            nested_config=config.nested_fields,
        )
        extracted.update(nested_data)

    return extracted
