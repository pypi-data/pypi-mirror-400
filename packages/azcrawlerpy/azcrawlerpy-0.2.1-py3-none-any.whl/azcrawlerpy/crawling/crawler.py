"""
Main FormCrawler class for navigating and filling multi-step web forms.

This module contains the core crawler implementation that orchestrates
field handlers and action executors to complete form workflows.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from playwright.async_api import (
    Error as PlaywrightError,
)
from playwright.async_api import (
    Page,
    async_playwright,
)
from playwright.async_api import (
    TimeoutError as PlaywrightTimeoutError,
)

from .actions import get_action_executor
from .browser_utils import handle_cookie_consent
from .config import DEFAULT_USER_AGENT, DEFAULT_VIEWPORT_HEIGHT, DEFAULT_VIEWPORT_WIDTH
from .data_extraction import _apply_regex, extract_data
from .diagnostics import CrawlContext, capture_page_diagnostics, write_diagnostic_json
from .exceptions import CrawlerError, CrawlerTimeoutError
from .field_handlers import get_field_handler
from .models import CrawlResult, DebugMode, InMemoryCrawlResult, Instructions, StepDefinition, StepExtractionDefinition
from .utils import setup_logger

logger = setup_logger(__name__)


@dataclass
class _CrawlState:
    """
    Internal state for a single crawl execution.

    Tracks debug configuration, output paths, screenshot numbering,
    in-memory results, and extracted data during the crawl lifecycle.
    """

    debug_mode: DebugMode
    output_dir: Path | None
    context: CrawlContext
    screenshot_counter: int = 0
    current_step_name: str | None = None
    in_memory_screenshots: list[bytes] = field(default_factory=list)
    extracted_data: dict[str, Any] = field(default_factory=dict)


class FormCrawler:
    """
    Crawler for navigating and filling multi-step web forms.

    This class provides the main interface for automating form completion
    based on JSON instructions. It handles:
    - Multi-step wizard forms
    - Various field types (text, dropdown, radio, etc.)
    - Navigation between form steps
    - Waiting for AJAX-loaded content
    - Saving final page HTML and screenshots
    """

    def __init__(self, headless: bool = True) -> None:
        """
        Initialize the crawler.

        Args:
            headless: Whether to run browser in headless mode

        """
        self._headless: bool = headless

    async def crawl(
        self,
        url: str,
        input_data: dict[str, Any],
        instructions: dict[str, Any],
        output_dir: Path | None = None,
        debug_mode: DebugMode = DebugMode.NONE,
    ) -> CrawlResult | InMemoryCrawlResult:
        """
        Navigate and fill the form, returning results.

        Args:
            url: Starting URL where the form begins
            input_data: Field values to fill (key-value pairs)
            instructions: Navigation and field selectors (JSON structure)
            output_dir: Directory to save HTML and screenshots. If None, returns in-memory result.
            debug_mode: Screenshot mode (none, start, end, all)

        Returns:
            CrawlResult with paths to saved files when output_dir is provided,
            InMemoryCrawlResult with in-memory data when output_dir is None.

        """
        validated_instructions = Instructions.model_validate(instructions)

        if output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)

        debug_enabled = debug_mode != DebugMode.NONE
        state = _CrawlState(
            debug_mode=debug_mode,
            output_dir=output_dir,
            context=CrawlContext(output_dir=output_dir, debug_enabled=debug_enabled),
        )

        logger.info(f"Starting crawl: url='{url}' steps={len(validated_instructions.steps)} debug='{debug_mode.value}'")
        logger.info(f"Id='{input_data.get('id', 'Test Run')}'")
        logger.info(f"subscriber='{input_data.get('subscriber', 'Test Run')}'")
        logger.info(f"url='{input_data.get('url', 'Test Run')}'")
        logger.info(f"dev_environment='{input_data.get('dev_environment', 'Test Run')}'")
        logger.info(f"lock='{input_data.get('lock', 'Test Run')}'")

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=self._headless)

            browser_config = validated_instructions.browser_config
            viewport_width = browser_config.viewport_width if browser_config else DEFAULT_VIEWPORT_WIDTH
            viewport_height = browser_config.viewport_height if browser_config else DEFAULT_VIEWPORT_HEIGHT
            user_agent = (
                browser_config.user_agent if browser_config and browser_config.user_agent else DEFAULT_USER_AGENT
            )

            browser_context = await browser.new_context(
                viewport={"width": viewport_width, "height": viewport_height},
                user_agent=user_agent,
            )
            page = await browser_context.new_page()

            self._setup_event_handlers(page=page, state=state)

            try:
                await page.goto(url=url, wait_until="networkidle")
                logger.info(f"Navigated to starting URL: url='{url}'")

                if validated_instructions.cookie_consent:
                    await handle_cookie_consent(
                        page=page,
                        config=validated_instructions.cookie_consent,
                    )

                if debug_mode in (DebugMode.START, DebugMode.ALL):
                    await self._take_debug_screenshot(page=page, label="start", state=state)

                steps_completed = 0
                for step in validated_instructions.steps:
                    await self._process_step(
                        page=page,
                        step=step,
                        input_data=input_data,
                        state=state,
                    )
                    steps_completed += 1

                return await self._capture_final_page(
                    page=page,
                    instructions=validated_instructions,
                    steps_completed=steps_completed,
                    url=url,
                    input_data=input_data,
                    raw_instructions=instructions,
                    state=state,
                )

            except CrawlerError as e:
                if state.context.debug_enabled:
                    await self._capture_error_diagnostics(page=page, error=e, state=state)
                raise

            finally:
                await browser_context.close()
                await browser.close()

    def _setup_event_handlers(self, page: Page, state: _CrawlState) -> None:
        """
        Set up console and network event handlers for diagnostic capture.

        Args:
            page: Playwright page instance
            state: Current crawl state containing the context to populate

        """

        def on_console(msg: Any) -> None:
            state.context.console_messages.append(
                {
                    "type": msg.type,
                    "text": msg.text,
                }
            )

        def on_request_failed(request: Any) -> None:
            state.context.failed_requests.append(
                {
                    "url": request.url,
                    "method": request.method,
                    "failure": request.failure,
                }
            )

        page.on("console", on_console)
        page.on("requestfailed", on_request_failed)

    async def _capture_error_diagnostics(
        self,
        page: Page,
        error: CrawlerError,
        state: _CrawlState,
    ) -> None:
        """
        Capture page diagnostics when an error occurs.

        Args:
            page: Playwright page instance
            error: The exception that triggered diagnostic capture
            state: Current crawl state with step context

        """
        failed_selector = getattr(error, "selector", None)
        step_name = state.current_step_name

        label = step_name if step_name else "unknown"

        diagnostics = await capture_page_diagnostics(
            page=page,
            context=state.context,
            failed_selector=failed_selector,
            step_name=step_name,
            label=label,
        )

        error.with_diagnostics(diagnostics)

        if state.output_dir is not None:
            write_diagnostic_json(
                output_dir=state.output_dir,
                error=error,
                diagnostics=diagnostics,
            )

    async def _take_debug_screenshot(self, page: Page, label: str, state: _CrawlState) -> None:
        """
        Take a debug screenshot with incrementing counter.

        Args:
            page: Playwright page instance
            label: Descriptive label for the screenshot filename
            state: Current crawl state for counter and output path

        """
        state.screenshot_counter += 1

        if state.output_dir is not None:
            filename = f"debug_{state.screenshot_counter:03d}_{label}.png"
            screenshot_path = state.output_dir / filename
            await page.screenshot(path=str(screenshot_path), full_page=True)
            logger.info(f"Debug screenshot: path='{screenshot_path}'")
        else:
            screenshot_bytes = await page.screenshot(full_page=True)
            state.in_memory_screenshots.append(screenshot_bytes)
            logger.info(f"Debug screenshot captured in-memory: label='{label}'")

    async def _extract_step_data(
        self,
        page: Page,
        extractions: list[StepExtractionDefinition],
        step_name: str,
        state: _CrawlState,
    ) -> None:
        """
        Extract data during a step and store in state.extracted_data.

        Args:
            page: Playwright page instance
            extractions: List of extraction definitions for this step
            step_name: Name of the current step (for logging)
            state: Current crawl state to store extracted data

        """
        for extraction in extractions:
            if extraction.wait_before_ms is not None:
                await page.wait_for_timeout(timeout=extraction.wait_before_ms)
                logger.info(f"Step extraction wait_before: ms={extraction.wait_before_ms} step='{step_name}'")

            if extraction.click_before is not None:
                if extraction.dismiss_modal_selector is not None and not extraction.force_click:
                    await page.click(selector=extraction.click_before, force=True)
                    logger.info(f"Step extraction click (force for modal): selector='{extraction.click_before}' step='{step_name}'")
                    await page.evaluate(f"document.querySelector('{extraction.click_before}').click()")
                    logger.info(f"Step extraction JS click: selector='{extraction.click_before}' step='{step_name}'")
                else:
                    await page.click(selector=extraction.click_before, force=extraction.force_click)
                    logger.info(f"Step extraction click: selector='{extraction.click_before}' force={extraction.force_click} step='{step_name}'")

                if extraction.wait_after_click_ms is not None:
                    await page.wait_for_timeout(timeout=extraction.wait_after_click_ms)

            locator = page.locator(extraction.selector)
            count = await locator.count()

            if count == 0:
                logger.warning(
                    f"Step extraction no match: name='{extraction.name}' selector='{extraction.selector}' step='{step_name}'"
                )
                state.extracted_data[extraction.name] = None
                continue

            element = locator.first
            raw_value = (
                await element.get_attribute(name=extraction.attribute)
                if extraction.attribute
                else await element.text_content()
            )

            processed_value = _apply_regex(value=raw_value, pattern=extraction.regex)
            state.extracted_data[extraction.name] = processed_value
            logger.info(
                f"Step extraction: name='{extraction.name}' value='{processed_value}' step='{step_name}'"
            )

            if extraction.dismiss_modal_selector is not None:
                modal_locator = page.locator(extraction.dismiss_modal_selector)
                if await modal_locator.count() > 0:
                    await modal_locator.first.click(force=True)
                    logger.info(f"Step extraction dismissed modal: selector='{extraction.dismiss_modal_selector}' step='{step_name}'")

    async def _process_step(
        self,
        page: Page,
        step: StepDefinition,
        input_data: dict[str, Any],
        state: _CrawlState,
    ) -> None:
        """
        Process a single form step.

        Waits for step selector, fills all fields, and executes the next action.

        Args:
            page: Playwright page instance
            step: Step definition with wait condition, fields, and action
            input_data: Field values to fill
            state: Current crawl state for debugging

        """
        state.current_step_name = step.name
        logger.info(f"Processing step: name='{step.name}'")

        try:
            await page.wait_for_selector(
                selector=step.wait_for,
                state="visible",
                timeout=step.timeout_ms,
            )
            logger.info(f"Wait condition met: selector='{step.wait_for}' step='{step.name}'")
        except (PlaywrightTimeoutError, PlaywrightError) as e:
            raise CrawlerTimeoutError(
                selector=step.wait_for,
                step_name=step.name,
                timeout_ms=step.timeout_ms,
            ) from e

        if step.data_extraction is not None:
            await self._extract_step_data(
                page=page,
                extractions=step.data_extraction,
                step_name=step.name,
                state=state,
            )

        for field_def in step.fields:
            handler = get_field_handler(field_type=field_def.type, step_name=step.name)
            await handler.handle(
                page=page,
                field=field_def,
                input_data=input_data,
                step_name=step.name,
            )

            if state.debug_mode == DebugMode.ALL:
                label = f"{step.name}_{field_def.data_key}"
                await self._take_debug_screenshot(page=page, label=label, state=state)

        if step.post_field_extraction is not None:
            await self._extract_step_data(
                page=page,
                extractions=step.post_field_extraction,
                step_name=step.name,
                state=state,
            )

        executor = get_action_executor(action_type=step.next_action.type, step_name=step.name)
        await executor.execute(
            page=page,
            action=step.next_action,
            step_name=step.name,
            input_data=input_data,
        )

        if state.debug_mode == DebugMode.ALL:
            await self._take_debug_screenshot(page=page, label=f"{step.name}_after_action", state=state)

        logger.info(f"Step completed: name='{step.name}'")

    async def _capture_final_page(
        self,
        page: Page,
        instructions: Instructions,
        steps_completed: int,
        url: str,
        input_data: dict[str, Any],
        raw_instructions: dict[str, Any],
        state: _CrawlState,
    ) -> CrawlResult | InMemoryCrawlResult:
        """
        Capture the final result page.

        Waits for final selector, extracts data, saves HTML and screenshot.

        Args:
            page: Playwright page instance
            instructions: Validated instructions with final page config
            steps_completed: Number of steps successfully processed
            url: Original starting URL
            input_data: Input data used for form filling
            raw_instructions: Original unvalidated instructions dict
            state: Current crawl state for output paths

        Returns:
            CrawlResult with file paths or InMemoryCrawlResult with bytes

        """
        final_page = instructions.final_page

        try:
            await page.wait_for_selector(
                selector=final_page.wait_for,
                state="visible",
                timeout=final_page.timeout_ms,
            )
            logger.info(f"Final page loaded: selector='{final_page.wait_for}'")
        except (PlaywrightTimeoutError, PlaywrightError) as e:
            raise CrawlerTimeoutError(
                selector=final_page.wait_for,
                step_name="final_page",
                timeout_ms=final_page.timeout_ms,
            ) from e

        if state.debug_mode in (DebugMode.END, DebugMode.ALL):
            await self._take_debug_screenshot(page=page, label="end", state=state)

        html_content = await page.content()
        final_url = page.url

        extracted_data: dict[str, Any] = dict(state.extracted_data)
        if instructions.data_extraction is not None:
            final_page_data = await extract_data(
                page=page,
                config=instructions.data_extraction,
            )
            extracted_data.update(final_page_data)
            logger.info(f"Final page extraction complete: fields_extracted={len(final_page_data)}")
        logger.info(f"Total extracted data: fields={len(extracted_data)}")

        if state.output_dir is not None:
            html_path = state.output_dir / "result.html"
            html_path.write_text(data=html_content, encoding="utf-8")
            logger.info(f"Saved HTML: path='{html_path}'")

            screenshot_path = state.output_dir / "result.png"
            if final_page.screenshot_selector:
                locator = page.locator(final_page.screenshot_selector)
                await locator.screenshot(path=str(screenshot_path))
            else:
                await page.screenshot(path=str(screenshot_path), full_page=True)
            logger.info(f"Saved screenshot: path='{screenshot_path}'")

            return CrawlResult(
                html_path=html_path,
                screenshot_path=screenshot_path,
                final_url=final_url,
                steps_completed=steps_completed,
                extracted_data=extracted_data,
            )

        if state.debug_mode != DebugMode.NONE:
            if final_page.screenshot_selector:
                locator = page.locator(final_page.screenshot_selector)
                final_screenshot = await locator.screenshot()
            else:
                final_screenshot = await page.screenshot(full_page=True)

            state.in_memory_screenshots.append(final_screenshot)
            logger.info("Captured final screenshot in-memory")

        return InMemoryCrawlResult(
            url=url,
            input_data=input_data,
            instructions=raw_instructions,
            screenshots=state.in_memory_screenshots,
            html=html_content,
            final_url=final_url,
            steps_completed=steps_completed,
            extracted_data=extracted_data,
        )
