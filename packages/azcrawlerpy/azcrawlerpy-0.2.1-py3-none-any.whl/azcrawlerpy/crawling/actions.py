"""
Action executors for navigation and interaction.

Each action class handles a specific action type (click, wait, scroll, etc.).
Uses dispatch pattern for action type routing.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any

from playwright.async_api import (
    Error as PlaywrightError,
)
from playwright.async_api import (
    Page,
)
from playwright.async_api import (
    TimeoutError as PlaywrightTimeoutError,
)

from .config import (
    ACTION_ELEMENT_ATTACHED_TIMEOUT_MS,
    ACTION_POST_DELAY_MS,
    ACTION_PRE_DELAY_MS,
    ACTION_WAIT_TIMEOUT_MS,
)
from .exceptions import CrawlerTimeoutError, NavigationError, UnsupportedActionTypeError
from .models import ActionDefinition, ActionType
from .utils import normalize_selector, setup_logger

logger = setup_logger(__name__)


class BaseActionExecutor(ABC):
    """
    Abstract base class for action executors.

    Subclasses implement specific action logic for each ActionType.
    """

    @abstractmethod
    async def execute(
        self,
        page: Page,
        action: ActionDefinition,
        step_name: str,
        input_data: dict[str, Any],
    ) -> None:
        """
        Execute the action.

        Args:
            page: Playwright page instance
            action: Action definition from instructions
            step_name: Current step name for error context
            input_data: Dictionary of field values (for conditional actions)

        """


class ClickActionExecutor(BaseActionExecutor):
    """Executor for click actions with configurable pre/post delays."""

    async def execute(
        self,
        page: Page,
        action: ActionDefinition,
        step_name: str,
        input_data: dict[str, Any],
    ) -> None:
        if not action.selector:
            raise NavigationError(
                step_name=step_name,
                action_type=action.type.value,
                selector="",
                reason="Click action requires a selector",
            )

        selector = normalize_selector(action.selector)

        pre_action_delay_ms = (
            action.pre_action_delay_ms if action.pre_action_delay_ms is not None else ACTION_PRE_DELAY_MS
        )
        post_action_delay_ms = (
            action.post_action_delay_ms if action.post_action_delay_ms is not None else ACTION_POST_DELAY_MS
        )

        try:
            await asyncio.sleep(pre_action_delay_ms / 1000)

            if action.iframe_selector:
                frame = page.frame_locator(action.iframe_selector)
                locator = frame.locator(selector)
            else:
                locator = page.locator(selector)

            await locator.wait_for(state="attached", timeout=ACTION_ELEMENT_ATTACHED_TIMEOUT_MS)
            await locator.scroll_into_view_if_needed()
            await locator.click()
            iframe_info = f" iframe='{action.iframe_selector}'" if action.iframe_selector else ""
            logger.info(f"Clicked element: selector='{selector}'{iframe_info} step='{step_name}'")

            await asyncio.sleep(post_action_delay_ms / 1000)
        except (PlaywrightTimeoutError, PlaywrightError) as e:
            raise NavigationError(
                step_name=step_name,
                action_type=action.type.value,
                selector=selector,
                reason=str(e),
            ) from e


class WaitActionExecutor(BaseActionExecutor):
    """Executor for wait actions that block until element becomes visible."""

    async def execute(
        self,
        page: Page,
        action: ActionDefinition,
        step_name: str,
        input_data: dict[str, Any],
    ) -> None:
        if not action.selector:
            raise NavigationError(
                step_name=step_name,
                action_type=action.type.value,
                selector="",
                reason="Wait action requires a selector",
            )

        selector = normalize_selector(action.selector)
        timeout_ms = action.delay_ms if action.delay_ms is not None else ACTION_WAIT_TIMEOUT_MS

        try:
            await page.wait_for_selector(selector=selector, state="visible", timeout=timeout_ms)
            logger.info(f"Wait completed: selector='{selector}' step='{step_name}'")
        except (PlaywrightTimeoutError, PlaywrightError) as e:
            raise CrawlerTimeoutError(
                selector=selector,
                step_name=step_name,
                timeout_ms=timeout_ms,
            ) from e


class WaitHiddenActionExecutor(BaseActionExecutor):
    """Executor for wait_hidden actions that block until element disappears."""

    async def execute(
        self,
        page: Page,
        action: ActionDefinition,
        step_name: str,
        input_data: dict[str, Any],
    ) -> None:
        if not action.selector:
            raise NavigationError(
                step_name=step_name,
                action_type=action.type.value,
                selector="",
                reason="Wait hidden action requires a selector",
            )

        selector = normalize_selector(action.selector)
        timeout_ms = action.delay_ms if action.delay_ms is not None else ACTION_WAIT_TIMEOUT_MS

        try:
            await page.wait_for_selector(selector=selector, state="hidden", timeout=timeout_ms)
            logger.info(f"Wait hidden completed: selector='{selector}' step='{step_name}'")
        except (PlaywrightTimeoutError, PlaywrightError) as e:
            raise CrawlerTimeoutError(
                selector=selector,
                step_name=step_name,
                timeout_ms=timeout_ms,
            ) from e


class ScrollActionExecutor(BaseActionExecutor):
    """Executor for scroll actions that bring target element into view."""

    async def execute(
        self,
        page: Page,
        action: ActionDefinition,
        step_name: str,
        input_data: dict[str, Any],
    ) -> None:
        if not action.selector:
            raise NavigationError(
                step_name=step_name,
                action_type=action.type.value,
                selector="",
                reason="Scroll action requires a selector",
            )

        selector = normalize_selector(action.selector)
        locator = page.locator(selector)

        try:
            await locator.scroll_into_view_if_needed()
            logger.info(f"Scrolled to element: selector='{selector}' step='{step_name}'")
        except (PlaywrightTimeoutError, PlaywrightError) as e:
            raise NavigationError(
                step_name=step_name,
                action_type=action.type.value,
                selector=selector,
                reason=str(e),
            ) from e


class DelayActionExecutor(BaseActionExecutor):
    """Executor for fixed delay actions using asyncio.sleep."""

    async def execute(
        self,
        page: Page,
        action: ActionDefinition,
        step_name: str,
        input_data: dict[str, Any],
    ) -> None:
        if not action.delay_ms:
            raise NavigationError(
                step_name=step_name,
                action_type=action.type.value,
                selector="",
                reason="Delay action requires delay_ms to be specified",
            )

        delay_seconds = action.delay_ms / 1000.0
        await asyncio.sleep(delay_seconds)
        logger.info(f"Delayed for {action.delay_ms}ms step='{step_name}'")


class ConditionalActionExecutor(BaseActionExecutor):
    """Executor for conditional actions that evaluate conditions and run nested actions."""

    async def execute(
        self,
        page: Page,
        action: ActionDefinition,
        step_name: str,
        input_data: dict[str, Any],
    ) -> None:
        if not action.condition:
            raise NavigationError(
                step_name=step_name,
                action_type=action.type.value,
                selector="",
                reason="Conditional action requires a condition",
            )

        if not action.actions:
            raise NavigationError(
                step_name=step_name,
                action_type=action.type.value,
                selector="",
                reason="Conditional action requires nested actions",
            )

        condition_met = await self._evaluate_condition(
            page=page,
            condition=action.condition,
            input_data=input_data,
        )

        if condition_met:
            logger.info(f"Condition met, executing nested actions: step='{step_name}'")
            for nested_action in action.actions:
                executor = get_action_executor(action_type=nested_action.type, step_name=step_name)
                await executor.execute(
                    page=page,
                    action=nested_action,
                    step_name=step_name,
                    input_data=input_data,
                )
        else:
            logger.info(f"Condition not met, skipping nested actions: step='{step_name}'")

    async def _evaluate_condition(
        self,
        page: Page,
        condition: dict[str, Any],
        input_data: dict[str, Any],
    ) -> bool:
        """
        Evaluate a condition dictionary.

        Args:
            page: Playwright page instance
            condition: Condition dict with type and parameters
            input_data: Input data for data-based conditions

        Returns:
            True if condition is met, False otherwise

        Supported condition types:
            - selector_visible: Check if selector is visible
            - selector_hidden: Check if selector is hidden
            - data_equals: Check if data key equals value
            - data_exists: Check if data key exists and is truthy

        """
        condition_type = condition.get("type")

        if condition_type == "selector_visible":
            selector = condition.get("selector")
            if not selector:
                return False
            try:
                return await page.locator(selector).is_visible()
            except PlaywrightTimeoutError:
                return False

        elif condition_type == "selector_hidden":
            selector = condition.get("selector")
            if not selector:
                return True
            try:
                is_visible = await page.locator(selector).is_visible()
                return not is_visible
            except PlaywrightTimeoutError:
                return True

        elif condition_type == "data_equals":
            data_key = condition.get("key")
            expected_value = condition.get("value")
            if not data_key:
                return False
            actual_value = input_data.get(data_key)
            return actual_value == expected_value

        elif condition_type == "data_exists":
            data_key = condition.get("key")
            if not data_key:
                return False
            return bool(input_data.get(data_key))

        return False


ACTION_EXECUTORS: dict[ActionType, type[BaseActionExecutor]] = {
    ActionType.CLICK: ClickActionExecutor,
    ActionType.WAIT: WaitActionExecutor,
    ActionType.WAIT_HIDDEN: WaitHiddenActionExecutor,
    ActionType.SCROLL: ScrollActionExecutor,
    ActionType.DELAY: DelayActionExecutor,
    ActionType.CONDITIONAL: ConditionalActionExecutor,
}


def get_action_executor(action_type: ActionType, step_name: str) -> BaseActionExecutor:
    """
    Get the appropriate executor for an action type.

    Args:
        action_type: ActionType enum value
        step_name: Current step name for error context

    Returns:
        Instantiated executor for the action type

    Raises:
        UnsupportedActionTypeError: If action_type has no registered executor

    """
    executor_class = ACTION_EXECUTORS.get(action_type)
    if executor_class is None:
        raise UnsupportedActionTypeError(
            action_type=action_type.value,
            step_name=step_name,
        )
    return executor_class()
