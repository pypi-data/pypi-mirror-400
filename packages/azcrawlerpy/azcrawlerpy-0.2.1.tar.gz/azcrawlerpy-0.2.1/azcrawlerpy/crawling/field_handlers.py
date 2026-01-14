"""
Field type handlers for form interactions.

Each handler class is responsible for a specific field type (text, dropdown, etc.).
Uses composition pattern with a dispatch dictionary for field type routing.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any

from playwright.async_api import (
    Error as PlaywrightError,
)
from playwright.async_api import (
    FrameLocator,
    Locator,
    Page,
)
from playwright.async_api import (
    TimeoutError as PlaywrightTimeoutError,
)

from .config import (
    COMBOBOX_POST_CLEAR_DELAY_SECONDS,
    COMBOBOX_POST_ENTER_DELAY_SECONDS,
    COMBOBOX_PRE_TYPE_DELAY_SECONDS,
    FIELD_OPTION_VISIBLE_TIMEOUT_MS,
    FIELD_POST_CLICK_DELAY_MS,
    FIELD_TYPE_DELAY_MS,
    FIELD_VISIBLE_TIMEOUT_MS,
    FIELD_WAIT_AFTER_CLICK_MS,
    FIELD_WAIT_AFTER_TYPE_MS,
)
from .exceptions import (
    FieldInteractionError,
    FieldNotFoundError,
    IframeNotFoundError,
    UnsupportedFieldTypeError,
)
from .models import FieldDefinition, FieldType
from .utils import format_date, get_value_for_field, interpolate_selector_value, setup_logger

logger = setup_logger(__name__)


class BaseFieldHandler(ABC):
    """
    Abstract base class for field handlers.

    Provides common methods for locating fields, ensuring visibility,
    and retrieving values from input data. Subclasses implement specific
    interaction logic for each field type.
    """

    @abstractmethod
    async def handle(
        self,
        page: Page,
        field: FieldDefinition,
        input_data: dict[str, Any],
        step_name: str,
    ) -> None:
        """
        Handle the field interaction.

        Args:
            page: Playwright page instance
            field: Field definition from instructions
            input_data: Dictionary of field values
            step_name: Current step name for error context

        """

    def _get_locator(
        self,
        page: Page,
        field: FieldDefinition,
        step_name: str,
    ) -> Locator:
        """
        Get the locator for a field, handling iframes if necessary.

        Args:
            page: Playwright page instance
            field: Field definition with selector and optional iframe_selector
            step_name: Current step name for error context

        Returns:
            Playwright Locator for the field element

        """
        if field.iframe_selector:
            try:
                frame_loc: FrameLocator = page.frame_locator(field.iframe_selector)
                locator = frame_loc.locator(field.selector)
            except (PlaywrightTimeoutError, PlaywrightError) as e:
                raise IframeNotFoundError(
                    iframe_selector=field.iframe_selector,
                    step_name=step_name,
                ) from e
        else:
            locator = page.locator(field.selector)

        return locator

    async def _ensure_visible(
        self,
        locator: Locator,
        field: FieldDefinition,
        step_name: str,
    ) -> None:
        """
        Ensure the field is visible before interaction.

        Args:
            locator: Playwright Locator for the field
            field: Field definition with optional visibility timeout
            step_name: Current step name for error context

        Raises:
            FieldNotFoundError: If field does not become visible within timeout

        """
        field_visible_timeout_ms = (
            field.field_visible_timeout_ms if field.field_visible_timeout_ms is not None else FIELD_VISIBLE_TIMEOUT_MS
        )
        try:
            await locator.wait_for(state="visible", timeout=field_visible_timeout_ms)
        except (PlaywrightTimeoutError, PlaywrightError) as e:
            raise FieldNotFoundError(
                selector=field.selector,
                step_name=step_name,
                field_type=field.type.value,
            ) from e

    def _get_value(
        self,
        field: FieldDefinition,
        input_data: dict[str, Any],
        step_name: str,
    ) -> Any | None:
        """
        Get the value for a field from input data.

        Args:
            field: Field definition with data_key
            input_data: Dictionary of field values
            step_name: Current step name (unused, kept for signature consistency)

        Returns:
            Field value from input_data, or None if field should be skipped

        """
        if field.data_key is None:
            return None
        return get_value_for_field(input_data=input_data, data_key=field.data_key)


class TextFieldHandler(BaseFieldHandler):
    """Handler for standard text input fields (text, email, password, etc.)."""

    async def handle(
        self,
        page: Page,
        field: FieldDefinition,
        input_data: dict[str, Any],
        step_name: str,
    ) -> None:
        value = self._get_value(field=field, input_data=input_data, step_name=step_name)
        if value is None:
            logger.info(f"Skipping text field: data_key='{field.data_key}' step='{step_name}'")
            return

        locator = self._get_locator(page=page, field=field, step_name=step_name)
        await self._ensure_visible(locator=locator, field=field, step_name=step_name)

        try:
            await locator.focus()
            await locator.fill(str(value))

            if field.skip_verification:
                logger.info(
                    f"Filled text field (verification skipped): selector='{field.selector}' value='{value}' step='{step_name}'"
                )
            else:
                actual_value = await locator.input_value()
                logger.info(
                    f"Filled text field: selector='{field.selector}' value='{value}' actual='{actual_value}' step='{step_name}'"
                )
        except (PlaywrightTimeoutError, PlaywrightError) as e:
            raise FieldInteractionError(
                selector=field.selector,
                step_name=step_name,
                field_type=field.type.value,
                reason=str(e),
            ) from e


class TextareaFieldHandler(BaseFieldHandler):
    """Handler for multi-line text areas."""

    async def handle(
        self,
        page: Page,
        field: FieldDefinition,
        input_data: dict[str, Any],
        step_name: str,
    ) -> None:
        value = self._get_value(field=field, input_data=input_data, step_name=step_name)
        if value is None:
            logger.info(f"Skipping textarea field: data_key='{field.data_key}' step='{step_name}'")
            return

        locator = self._get_locator(page=page, field=field, step_name=step_name)
        await self._ensure_visible(locator=locator, field=field, step_name=step_name)

        try:
            await locator.fill(str(value))
            logger.info(f"Filled textarea: selector='{field.selector}' step='{step_name}'")
        except (PlaywrightTimeoutError, PlaywrightError) as e:
            raise FieldInteractionError(
                selector=field.selector,
                step_name=step_name,
                field_type=field.type.value,
                reason=str(e),
            ) from e


class DropdownFieldHandler(BaseFieldHandler):
    """Handler for native HTML select elements with option selection."""

    async def handle(
        self,
        page: Page,
        field: FieldDefinition,
        input_data: dict[str, Any],
        step_name: str,
    ) -> None:
        value = self._get_value(field=field, input_data=input_data, step_name=step_name)
        if value is None:
            logger.info(f"Skipping dropdown field: data_key='{field.data_key}' step='{step_name}'")
            return

        locator = self._get_locator(page=page, field=field, step_name=step_name)
        await self._ensure_visible(locator=locator, field=field, step_name=step_name)

        try:
            select_by = field.select_by if field.select_by else "text"

            if select_by == "value":
                await locator.select_option(value=str(value))
            elif select_by == "index":
                await locator.select_option(index=int(value))
            else:
                await locator.select_option(label=str(value))

            logger.info(f"Selected dropdown option: selector='{field.selector}' value='{value}' step='{step_name}'")
        except (PlaywrightTimeoutError, PlaywrightError) as e:
            raise FieldInteractionError(
                selector=field.selector,
                step_name=step_name,
                field_type=field.type.value,
                reason=str(e),
            ) from e


class RadioFieldHandler(BaseFieldHandler):
    """Handler for radio button selection with optional force click."""

    async def handle(
        self,
        page: Page,
        field: FieldDefinition,
        input_data: dict[str, Any],
        step_name: str,
    ) -> None:
        value = self._get_value(field=field, input_data=input_data, step_name=step_name)
        if value is None:
            logger.info(f"Skipping radio field: data_key='{field.data_key}' step='{step_name}'")
            return

        locator = self._get_locator(page=page, field=field, step_name=step_name)
        await self._ensure_visible(locator=locator, field=field, step_name=step_name)

        try:
            if field.force_click:
                await locator.click(force=True)
                logger.info(
                    f"Selected radio option (force click): selector='{field.selector}' value='{value}' step='{step_name}'"
                )
            else:
                await locator.check()
                logger.info(f"Selected radio option: selector='{field.selector}' value='{value}' step='{step_name}'")

            if field.post_click_delay_ms is not None:
                await asyncio.sleep(field.post_click_delay_ms / 1000)
        except (PlaywrightTimeoutError, PlaywrightError) as e:
            raise FieldInteractionError(
                selector=field.selector,
                step_name=step_name,
                field_type=field.type.value,
                reason=str(e),
            ) from e


class CheckboxFieldHandler(BaseFieldHandler):
    """Handler for checkbox fields with check/uncheck based on boolean value."""

    async def handle(
        self,
        page: Page,
        field: FieldDefinition,
        input_data: dict[str, Any],
        step_name: str,
    ) -> None:
        value = self._get_value(field=field, input_data=input_data, step_name=step_name)
        if value is None:
            logger.info(f"Skipping checkbox field: data_key='{field.data_key}' step='{step_name}'")
            return

        locator = self._get_locator(page=page, field=field, step_name=step_name)
        await self._ensure_visible(locator=locator, field=field, step_name=step_name)

        try:
            should_check = bool(value)
            if should_check:
                await locator.check()
            else:
                await locator.uncheck()
            logger.info(f"Set checkbox: selector='{field.selector}' checked={should_check} step='{step_name}'")
        except (PlaywrightTimeoutError, PlaywrightError) as e:
            raise FieldInteractionError(
                selector=field.selector,
                step_name=step_name,
                field_type=field.type.value,
                reason=str(e),
            ) from e


class DateFieldHandler(BaseFieldHandler):
    """Handler for date input fields with format conversion."""

    async def handle(
        self,
        page: Page,
        field: FieldDefinition,
        input_data: dict[str, Any],
        step_name: str,
    ) -> None:
        value = self._get_value(field=field, input_data=input_data, step_name=step_name)
        if value is None:
            logger.info(f"Skipping date field: data_key='{field.data_key}' step='{step_name}'")
            return

        locator = self._get_locator(page=page, field=field, step_name=step_name)
        await self._ensure_visible(locator=locator, field=field, step_name=step_name)

        try:
            input_type = await locator.get_attribute("type")
            is_native_date_input = input_type == "date"

            if is_native_date_input:
                fill_value = str(value)
                logger.info(f"Native date input detected, using ISO format: {fill_value}")
            elif field.format:
                fill_value = format_date(value=str(value), target_format=field.format)
            else:
                fill_value = str(value)

            await locator.fill(fill_value)
            logger.info(f"Filled date field: selector='{field.selector}' value='{fill_value}' step='{step_name}'")
        except (PlaywrightTimeoutError, PlaywrightError) as e:
            raise FieldInteractionError(
                selector=field.selector,
                step_name=step_name,
                field_type=field.type.value,
                reason=str(e),
            ) from e


class SliderFieldHandler(BaseFieldHandler):
    """Handler for range slider fields."""

    async def handle(
        self,
        page: Page,
        field: FieldDefinition,
        input_data: dict[str, Any],
        step_name: str,
    ) -> None:
        value = self._get_value(field=field, input_data=input_data, step_name=step_name)
        if value is None:
            logger.info(f"Skipping slider field: data_key='{field.data_key}' step='{step_name}'")
            return

        locator = self._get_locator(page=page, field=field, step_name=step_name)
        await self._ensure_visible(locator=locator, field=field, step_name=step_name)

        try:
            await locator.fill(str(value))
            logger.info(f"Set slider value: selector='{field.selector}' value='{value}' step='{step_name}'")
        except (PlaywrightTimeoutError, PlaywrightError) as e:
            raise FieldInteractionError(
                selector=field.selector,
                step_name=step_name,
                field_type=field.type.value,
                reason=str(e),
            ) from e


class FileFieldHandler(BaseFieldHandler):
    """Handler for file upload fields using file path from input data."""

    async def handle(
        self,
        page: Page,
        field: FieldDefinition,
        input_data: dict[str, Any],
        step_name: str,
    ) -> None:
        value = self._get_value(field=field, input_data=input_data, step_name=step_name)
        if value is None:
            logger.info(f"Skipping file field: data_key='{field.data_key}' step='{step_name}'")
            return

        locator = self._get_locator(page=page, field=field, step_name=step_name)
        await self._ensure_visible(locator=locator, field=field, step_name=step_name)

        try:
            file_path = str(value)
            await locator.set_input_files(file_path)
            logger.info(f"Uploaded file: selector='{field.selector}' path='{file_path}' step='{step_name}'")
        except (PlaywrightTimeoutError, PlaywrightError) as e:
            raise FieldInteractionError(
                selector=field.selector,
                step_name=step_name,
                field_type=field.type.value,
                reason=str(e),
            ) from e


class IframeFieldHandler(BaseFieldHandler):
    """Handler for text fields inside iframes requiring iframe_selector."""

    async def handle(
        self,
        page: Page,
        field: FieldDefinition,
        input_data: dict[str, Any],
        step_name: str,
    ) -> None:
        value = self._get_value(field=field, input_data=input_data, step_name=step_name)
        if value is None:
            logger.info(f"Skipping iframe field: data_key='{field.data_key}' step='{step_name}'")
            return

        if not field.iframe_selector:
            raise FieldInteractionError(
                selector=field.selector,
                step_name=step_name,
                field_type=field.type.value,
                reason="iframe_field type requires iframe_selector to be specified",
            )

        locator = self._get_locator(page=page, field=field, step_name=step_name)
        await self._ensure_visible(locator=locator, field=field, step_name=step_name)

        try:
            await locator.fill(str(value))
            logger.info(
                f"Filled iframe field: iframe='{field.iframe_selector}' selector='{field.selector}' step='{step_name}'"
            )
        except (PlaywrightTimeoutError, PlaywrightError) as e:
            raise FieldInteractionError(
                selector=field.selector,
                step_name=step_name,
                field_type=field.type.value,
                reason=str(e),
            ) from e


class ClickOnlyFieldHandler(BaseFieldHandler):
    """Handler for click-only elements with optional value-driven selector interpolation."""

    async def handle(
        self,
        page: Page,
        field: FieldDefinition,
        input_data: dict[str, Any],
        step_name: str,
    ) -> None:
        value = self._get_value(field=field, input_data=input_data, step_name=step_name)
        selector = field.selector
        has_value_placeholder = "${value}" in selector

        if field.data_key is not None and value is None:
            logger.info(f"Skipping click_only field: data_key='{field.data_key}' step='{step_name}'")
            return

        if has_value_placeholder:
            if value is None:
                raise FieldInteractionError(
                    selector=selector,
                    step_name=step_name,
                    field_type=field.type.value,
                    reason="Selector contains ${value} placeholder but no data_key specified or value is null",
                )
            selector = interpolate_selector_value(selector=selector, value=str(value))

        if field.iframe_selector:
            frame_loc = page.frame_locator(field.iframe_selector)
            locator = frame_loc.locator(selector)
        else:
            locator = page.locator(selector)

        await self._ensure_visible(locator=locator, field=field, step_name=step_name)

        post_click_delay_ms = (
            field.post_click_delay_ms if field.post_click_delay_ms is not None else FIELD_POST_CLICK_DELAY_MS
        )

        try:
            if field.force_click:
                await locator.click(force=True)
                logger.info(f"Clicked element (force click): selector='{selector}' step='{step_name}'")
            else:
                await locator.click()
                logger.info(f"Clicked element: selector='{selector}' step='{step_name}'")

            await asyncio.sleep(post_click_delay_ms / 1000)
        except (PlaywrightTimeoutError, PlaywrightError) as e:
            raise FieldInteractionError(
                selector=selector,
                step_name=step_name,
                field_type=field.type.value,
                reason=str(e),
            ) from e


class ComboboxFieldHandler(BaseFieldHandler):
    """Handler for combobox/autocomplete fields using type-wait-select pattern."""

    async def handle(
        self,
        page: Page,
        field: FieldDefinition,
        input_data: dict[str, Any],
        step_name: str,
    ) -> None:
        value = self._get_value(field=field, input_data=input_data, step_name=step_name)
        if value is None:
            logger.info(f"Skipping combobox field: data_key='{field.data_key}' step='{step_name}'")
            return

        locator = self._get_locator(page=page, field=field, step_name=step_name)
        await self._ensure_visible(locator=locator, field=field, step_name=step_name)

        type_delay_ms = field.type_delay_ms if field.type_delay_ms is not None else FIELD_TYPE_DELAY_MS
        wait_after_type_ms = field.wait_after_type_ms if field.wait_after_type_ms is not None else FIELD_WAIT_AFTER_TYPE_MS

        try:
            await locator.click()
            await asyncio.sleep(COMBOBOX_PRE_TYPE_DELAY_SECONDS)

            if field.clear_before_type:
                await locator.clear()
                await asyncio.sleep(COMBOBOX_POST_CLEAR_DELAY_SECONDS)

            if type_delay_ms > 0:
                await locator.press_sequentially(str(value), delay=type_delay_ms)
            else:
                await locator.fill(str(value))

            await asyncio.sleep(wait_after_type_ms / 1000)

            option_context: Page | FrameLocator = page
            if field.iframe_selector:
                option_context = page.frame_locator(field.iframe_selector)

            option_visible_timeout_ms = (
                field.option_visible_timeout_ms
                if field.option_visible_timeout_ms is not None
                else FIELD_OPTION_VISIBLE_TIMEOUT_MS
            )
            if field.option_selector:
                selector = interpolate_selector_value(selector=field.option_selector, value=str(value))
                option_locator = option_context.locator(selector).first
            else:
                option_locator = option_context.locator(f"text={value}").first

            await option_locator.wait_for(state="visible", timeout=option_visible_timeout_ms)
            await option_locator.click()

            if field.press_enter:
                await locator.press("Enter")
                await asyncio.sleep(COMBOBOX_POST_ENTER_DELAY_SECONDS)

            logger.info(f"Filled combobox: selector='{field.selector}' value='{value}' step='{step_name}'")
        except (PlaywrightTimeoutError, PlaywrightError) as e:
            raise FieldInteractionError(
                selector=field.selector,
                step_name=step_name,
                field_type=field.type.value,
                reason=str(e),
            ) from e


class ClickSelectFieldHandler(BaseFieldHandler):
    """Handler for custom dropdown components using click-to-open, select-option pattern."""

    async def handle(
        self,
        page: Page,
        field: FieldDefinition,
        input_data: dict[str, Any],
        step_name: str,
    ) -> None:
        value = self._get_value(field=field, input_data=input_data, step_name=step_name)
        if value is None:
            logger.info(f"Skipping click_select field: data_key='{field.data_key}' step='{step_name}'")
            return

        locator = self._get_locator(page=page, field=field, step_name=step_name)
        await self._ensure_visible(locator=locator, field=field, step_name=step_name)

        post_click_delay_ms = (
            field.post_click_delay_ms if field.post_click_delay_ms is not None else FIELD_WAIT_AFTER_CLICK_MS
        )

        try:
            await locator.click()
            await asyncio.sleep(post_click_delay_ms / 1000)

            option_context: Page | FrameLocator = page
            if field.iframe_selector:
                option_context = page.frame_locator(field.iframe_selector)

            option_visible_timeout_ms = (
                field.option_visible_timeout_ms
                if field.option_visible_timeout_ms is not None
                else FIELD_OPTION_VISIBLE_TIMEOUT_MS
            )
            if field.option_selector:
                selector = interpolate_selector_value(selector=field.option_selector, value=str(value))
                option_locator = option_context.locator(selector).first
            else:
                escaped_value = str(value).replace("'", "\\'")
                option_locator = option_context.locator(f"[role='option']:has-text('{escaped_value}')").first

            await option_locator.wait_for(state="visible", timeout=option_visible_timeout_ms)
            await option_locator.click()

            logger.info(f"Selected click_select option: selector='{field.selector}' value='{value}' step='{step_name}'")
        except (PlaywrightTimeoutError, PlaywrightError) as e:
            raise FieldInteractionError(
                selector=field.selector,
                step_name=step_name,
                field_type=field.type.value,
                reason=str(e),
            ) from e


FIELD_HANDLERS: dict[FieldType, type[BaseFieldHandler]] = {
    FieldType.TEXT: TextFieldHandler,
    FieldType.TEXTAREA: TextareaFieldHandler,
    FieldType.DROPDOWN: DropdownFieldHandler,
    FieldType.SELECT: DropdownFieldHandler,
    FieldType.RADIO: RadioFieldHandler,
    FieldType.CHECKBOX: CheckboxFieldHandler,
    FieldType.DATE: DateFieldHandler,
    FieldType.SLIDER: SliderFieldHandler,
    FieldType.FILE: FileFieldHandler,
    FieldType.IFRAME_FIELD: IframeFieldHandler,
    FieldType.CLICK_ONLY: ClickOnlyFieldHandler,
    FieldType.COMBOBOX: ComboboxFieldHandler,
    FieldType.CLICK_SELECT: ClickSelectFieldHandler,
}


def get_field_handler(field_type: FieldType, step_name: str) -> BaseFieldHandler:
    """
    Get the appropriate handler for a field type.

    Args:
        field_type: FieldType enum value
        step_name: Current step name for error context

    Returns:
        Instantiated handler for the field type

    Raises:
        UnsupportedFieldTypeError: If field_type has no registered handler

    """
    handler_class = FIELD_HANDLERS.get(field_type)
    if handler_class is None:
        raise UnsupportedFieldTypeError(
            field_type=field_type.value,
            step_name=step_name,
        )
    return handler_class()
