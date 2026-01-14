"""
Element discovery for web pages.

Scans a web page and discovers all interactive elements,
outputting a structured report for building instructions.json files.
"""

from datetime import datetime
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

from .browser_utils import handle_cookie_consent
from .config import DEFAULT_USER_AGENT, DISCOVERY_PAGE_LOAD_TIMEOUT_MS
from .discovery_models import (
    DiscoveredElement,
    ElementVisibility,
    IframeDiscovery,
    PageDiscoveryReport,
    RadioButtonGroup,
)
from .models import CookieConsentConfig, FieldType
from .utils import escape_css_id, setup_logger

logger = setup_logger(__name__)

INPUT_TYPE_TO_FIELD_TYPE: dict[str, FieldType] = {
    "text": FieldType.TEXT,
    "email": FieldType.TEXT,
    "password": FieldType.TEXT,
    "tel": FieldType.TEXT,
    "url": FieldType.TEXT,
    "number": FieldType.TEXT,
    "search": FieldType.TEXT,
    "date": FieldType.DATE,
    "datetime-local": FieldType.DATE,
    "month": FieldType.DATE,
    "week": FieldType.DATE,
    "time": FieldType.DATE,
    "file": FieldType.FILE,
    "range": FieldType.SLIDER,
    "checkbox": FieldType.CHECKBOX,
    "radio": FieldType.RADIO,
}


class ElementDiscovery:
    """
    Discovers interactive elements on a web page.

    Scans the page for all form elements, buttons, links, and custom
    components, producing a structured report for instruction authoring.
    """

    def __init__(self, headless: bool = True) -> None:
        """
        Initialize the discovery engine.

        Args:
            headless: Whether to run browser in headless mode

        """
        self._headless: bool = headless

    async def discover(
        self,
        url: str,
        output_dir: Path | None = None,
        cookie_consent: dict[str, Any] | None = None,
        explore_iframes: bool = True,
        screenshot: bool = True,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        wait_timeout_ms: int | None = None,
    ) -> PageDiscoveryReport:
        """
        Discover all interactive elements on a page.

        Args:
            url: URL to explore
            output_dir: Directory for output files (screenshots, JSON)
            cookie_consent: Cookie consent config dict (same format as instructions.json)
            explore_iframes: Whether to explore inside iframes
            screenshot: Whether to capture a screenshot
            viewport_width: Browser viewport width
            viewport_height: Browser viewport height
            wait_timeout_ms: Timeout for page load

        Returns:
            PageDiscoveryReport with all discovered elements

        """
        logger.info(f"Starting element discovery: url='{url}'")

        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)

        timeout_ms = wait_timeout_ms if wait_timeout_ms is not None else DISCOVERY_PAGE_LOAD_TIMEOUT_MS

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=self._headless)
            context = await browser.new_context(
                viewport={"width": viewport_width, "height": viewport_height},
                user_agent=DEFAULT_USER_AGENT,
            )
            page = await context.new_page()

            try:
                await page.goto(url=url, wait_until="networkidle", timeout=timeout_ms)
                logger.info(f"Navigated to URL: url='{url}'")

                if cookie_consent:
                    config = CookieConsentConfig.model_validate(cookie_consent)
                    await handle_cookie_consent(page=page, config=config)

                raw_elements = await self._capture_all_elements(page=page)
                categorized = self._categorize_elements(raw_elements=raw_elements)

                iframes: list[IframeDiscovery] = []
                if explore_iframes:
                    iframes = await self._discover_iframes(
                        page=page,
                        iframe_infos=raw_elements.get("iframes", []),
                    )

                screenshot_path: str | None = None
                if screenshot and output_dir:
                    screenshot_file = output_dir / "discovery_screenshot.png"
                    await page.screenshot(path=str(screenshot_file), full_page=True)
                    screenshot_path = str(screenshot_file)
                    logger.info(f"Screenshot saved: path='{screenshot_path}'")

                title = await page.title()
                timestamp = datetime.now().isoformat(timespec="seconds")

                total_elements = (
                    len(categorized["text_inputs"])
                    + len(categorized["textareas"])
                    + len(categorized["selects"])
                    + sum(len(rg.options) for rg in categorized["radio_groups"])
                    + len(categorized["checkboxes"])
                    + len(categorized["buttons"])
                    + len(categorized["links"])
                    + len(categorized["date_inputs"])
                    + len(categorized["file_inputs"])
                    + len(categorized["sliders"])
                    + len(categorized["custom_components"])
                    + sum(len(iframe.elements) for iframe in iframes)
                )

                return PageDiscoveryReport(
                    url=url,
                    title=title,
                    timestamp=timestamp,
                    text_inputs=categorized["text_inputs"],
                    textareas=categorized["textareas"],
                    selects=categorized["selects"],
                    radio_groups=categorized["radio_groups"],
                    checkboxes=categorized["checkboxes"],
                    buttons=categorized["buttons"],
                    links=categorized["links"],
                    date_inputs=categorized["date_inputs"],
                    file_inputs=categorized["file_inputs"],
                    sliders=categorized["sliders"],
                    custom_components=categorized["custom_components"],
                    iframes=iframes,
                    total_elements=total_elements,
                    screenshot_path=screenshot_path,
                )

            finally:
                await context.close()
                await browser.close()

    async def _capture_all_elements(self, page: Page) -> dict[str, Any]:
        """
        Capture all interactive elements using JavaScript evaluation.

        Args:
            page: Playwright page instance to scan

        Returns:
            Dict with 'elements' list and 'iframes' list from JS evaluation

        """
        return await page.evaluate(
            """
            () => {
                const results = [];

                function getVisibility(el) {
                    const rect = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);
                    const isVisible = rect.width > 0 && rect.height > 0 &&
                                      style.visibility !== 'hidden' &&
                                      style.display !== 'none';
                    if (!isVisible) return 'hidden';
                    const isOnScreen = rect.top < window.innerHeight && rect.bottom > 0 &&
                                       rect.left < window.innerWidth && rect.right > 0;
                    return isOnScreen ? 'visible' : 'off_screen';
                }

                function findLabelText(el) {
                    if (el.id) {
                        const label = document.querySelector(`label[for="${el.id}"]`);
                        if (label) return label.textContent?.trim() || null;
                    }
                    const parent = el.closest('label');
                    if (parent) return parent.textContent?.trim() || null;
                    return null;
                }

                function getSelectOptions(el) {
                    if (el.tagName !== 'SELECT') return { count: null, preview: null };
                    const options = el.querySelectorAll('option');
                    return {
                        count: options.length,
                        preview: Array.from(options).slice(0, 5).map(o => o.textContent?.trim()).filter(Boolean)
                    };
                }

                function getElementInfo(el, category) {
                    const rect = el.getBoundingClientRect();
                    const options = getSelectOptions(el);

                    return {
                        category: category,
                        tagName: el.tagName.toLowerCase(),
                        id: el.id || null,
                        name: el.getAttribute('name') || null,
                        type: el.getAttribute('type') || null,
                        dataCy: el.getAttribute('data-cy') || null,
                        dataTestid: el.getAttribute('data-testid') || null,
                        dataQa: el.getAttribute('data-qa') || null,
                        placeholder: el.getAttribute('placeholder') || null,
                        ariaLabel: el.getAttribute('aria-label') || null,
                        labelText: findLabelText(el),
                        textContent: el.textContent?.trim().substring(0, 100) || null,
                        href: el.getAttribute('href') || null,
                        visibility: getVisibility(el),
                        boundingBox: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
                        optionCount: options.count,
                        optionsPreview: options.preview
                    };
                }

                // Text inputs
                const textTypes = ['text', 'email', 'password', 'tel', 'url', 'number', 'search'];
                document.querySelectorAll(
                    textTypes.map(t => `input[type="${t}"]`).join(',') + ',input:not([type])'
                ).forEach(el => {
                    const type = el.getAttribute('type') || 'text';
                    if (!['hidden', 'submit', 'button', 'reset', 'checkbox', 'radio', 'file', 'range', 'date', 'datetime-local', 'month', 'week', 'time'].includes(type)) {
                        results.push(getElementInfo(el, 'text_input'));
                    }
                });

                // Date inputs
                document.querySelectorAll(
                    'input[type="date"], input[type="datetime-local"], input[type="month"], input[type="week"], input[type="time"]'
                ).forEach(el => results.push(getElementInfo(el, 'date_input')));

                // Textareas
                document.querySelectorAll('textarea').forEach(el => results.push(getElementInfo(el, 'textarea')));

                // Selects
                document.querySelectorAll('select').forEach(el => results.push(getElementInfo(el, 'select')));

                // Radio buttons
                document.querySelectorAll('input[type="radio"]').forEach(el => results.push(getElementInfo(el, 'radio')));

                // Checkboxes
                document.querySelectorAll('input[type="checkbox"]').forEach(el => results.push(getElementInfo(el, 'checkbox')));

                // File inputs
                document.querySelectorAll('input[type="file"]').forEach(el => results.push(getElementInfo(el, 'file_input')));

                // Range/slider inputs
                document.querySelectorAll('input[type="range"]').forEach(el => results.push(getElementInfo(el, 'range_input')));

                // Buttons
                document.querySelectorAll('button, input[type="submit"], input[type="button"]').forEach(el => {
                    results.push(getElementInfo(el, 'button'));
                });

                // Links
                document.querySelectorAll('a[href]').forEach(el => results.push(getElementInfo(el, 'link')));

                // Custom components (only add if not already captured)
                const capturedIds = new Set(results.map(r => `${r.id}-${r.dataCy}-${r.dataTestid}-${r.dataQa}`));
                document.querySelectorAll('[data-cy], [data-testid], [data-qa]').forEach(el => {
                    const key = `${el.id || ''}-${el.getAttribute('data-cy') || ''}-${el.getAttribute('data-testid') || ''}-${el.getAttribute('data-qa') || ''}`;
                    if (!capturedIds.has(key)) {
                        results.push(getElementInfo(el, 'custom_component'));
                        capturedIds.add(key);
                    }
                });

                // Iframes
                const iframes = Array.from(document.querySelectorAll('iframe')).map(iframe => ({
                    selector: iframe.id ? `#${iframe.id}` :
                              iframe.name ? `iframe[name="${iframe.name}"]` :
                              iframe.src ? `iframe[src*="${iframe.src.split('/').pop()?.split('?')[0] || ''}"]` : null,
                    src: iframe.src || null,
                    name: iframe.name || null
                }));

                return { elements: results, iframes: iframes };
            }
            """
        )

    def _categorize_elements(
        self,
        raw_elements: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Categorize raw elements into typed lists by element category.

        Args:
            raw_elements: Dict from _capture_all_elements with 'elements' key

        Returns:
            Dict with categorized element lists and radio_groups

        """
        elements = raw_elements.get("elements", [])

        categorized: dict[str, list[Any]] = {
            "text_inputs": [],
            "textareas": [],
            "selects": [],
            "radios": [],
            "checkboxes": [],
            "buttons": [],
            "links": [],
            "date_inputs": [],
            "file_inputs": [],
            "sliders": [],
            "custom_components": [],
        }

        category_to_key: dict[str, str] = {
            "text_input": "text_inputs",
            "textarea": "textareas",
            "select": "selects",
            "radio": "radios",
            "checkbox": "checkboxes",
            "button": "buttons",
            "link": "links",
            "date_input": "date_inputs",
            "file_input": "file_inputs",
            "range_input": "sliders",
            "custom_component": "custom_components",
        }

        for elem in elements:
            category = elem.get("category")
            target_key = category_to_key.get(category)
            if target_key is None:
                continue

            if category == "radio":
                categorized[target_key].append(elem)
            else:
                discovered = self._create_discovered_element(raw=elem)
                categorized[target_key].append(discovered)

        radio_groups = self._group_radio_buttons(radios=categorized["radios"])

        return {
            "text_inputs": categorized["text_inputs"],
            "textareas": categorized["textareas"],
            "selects": categorized["selects"],
            "radio_groups": radio_groups,
            "checkboxes": categorized["checkboxes"],
            "buttons": categorized["buttons"],
            "links": categorized["links"],
            "date_inputs": categorized["date_inputs"],
            "file_inputs": categorized["file_inputs"],
            "sliders": categorized["sliders"],
            "custom_components": categorized["custom_components"],
        }

    def _create_discovered_element(self, raw: dict[str, Any]) -> DiscoveredElement:
        """
        Create a DiscoveredElement from raw JavaScript data.

        Args:
            raw: Element dict from JavaScript evaluation

        Returns:
            Populated DiscoveredElement with selector and metadata

        """
        selector, alternatives = self._build_selector(raw=raw)
        field_type = self._map_to_field_type(
            tag_name=raw.get("tagName", ""),
            input_type=raw.get("type"),
            category=raw.get("category"),
        )

        visibility_str = raw.get("visibility", "hidden")
        try:
            visibility = ElementVisibility(visibility_str)
        except ValueError:
            logger.warning(f"Unknown visibility value: visibility='{visibility_str}', defaulting to 'hidden'")
            visibility = ElementVisibility.HIDDEN

        return DiscoveredElement(
            tag_name=raw.get("tagName", "unknown"),
            suggested_field_type=field_type,
            selector=selector,
            alternative_selectors=alternatives,
            element_id=raw.get("id"),
            name=raw.get("name"),
            input_type=raw.get("type"),
            data_cy=raw.get("dataCy"),
            data_testid=raw.get("dataTestid"),
            data_qa=raw.get("dataQa"),
            label_text=raw.get("labelText"),
            placeholder=raw.get("placeholder"),
            aria_label=raw.get("ariaLabel"),
            text_content=raw.get("textContent"),
            visibility=visibility,
            bounding_box=raw.get("boundingBox"),
            option_count=raw.get("optionCount"),
            options_preview=raw.get("optionsPreview"),
            group_name=raw.get("name"),
            href=raw.get("href"),
        )

    def _build_selector(self, raw: dict[str, Any]) -> tuple[str, list[str]]:
        """
        Build the best selector and alternatives for an element.

        Priority: data-cy > data-testid > data-qa > id > name > tag combo

        Returns:
            Tuple of (primary_selector, alternative_selectors)

        """
        alternatives: list[str] = []

        data_cy = raw.get("dataCy")
        data_testid = raw.get("dataTestid")
        data_qa = raw.get("dataQa")
        element_id = raw.get("id")
        name = raw.get("name")
        tag_name = raw.get("tagName", "")
        input_type = raw.get("type")

        if data_cy:
            primary = f"[data-cy='{data_cy}']"
            if data_testid:
                alternatives.append(f"[data-testid='{data_testid}']")
            if data_qa:
                alternatives.append(f"[data-qa='{data_qa}']")
            if element_id:
                alternatives.append(f"#{escape_css_id(element_id)}")
            if name:
                alternatives.append(f"{tag_name}[name='{name}']")
            return primary, alternatives

        if data_testid:
            primary = f"[data-testid='{data_testid}']"
            if data_qa:
                alternatives.append(f"[data-qa='{data_qa}']")
            if element_id:
                alternatives.append(f"#{escape_css_id(element_id)}")
            if name:
                alternatives.append(f"{tag_name}[name='{name}']")
            return primary, alternatives

        if data_qa:
            primary = f"[data-qa='{data_qa}']"
            if element_id:
                alternatives.append(f"#{escape_css_id(element_id)}")
            if name:
                alternatives.append(f"{tag_name}[name='{name}']")
            return primary, alternatives

        if element_id:
            primary = f"#{escape_css_id(element_id)}"
            if name:
                alternatives.append(f"{tag_name}[name='{name}']")
            return primary, alternatives

        if name:
            primary = f"{tag_name}[name='{name}']"
            if input_type:
                alternatives.append(f"{tag_name}[type='{input_type}'][name='{name}']")
            return primary, alternatives

        if input_type:
            primary = f"{tag_name}[type='{input_type}']"
        else:
            primary = tag_name

        return primary, alternatives


    def _map_to_field_type(
        self,
        tag_name: str,
        input_type: str | None,
        category: str | None,
    ) -> FieldType | None:
        """
        Map HTML element to FieldType enum value.

        Args:
            tag_name: HTML tag name (lowercase)
            input_type: Input type attribute value
            category: Element category from JS evaluation

        Returns:
            Matching FieldType or None for unmapped elements

        """
        if tag_name == "textarea":
            return FieldType.TEXTAREA

        if tag_name == "select":
            return FieldType.SELECT

        if tag_name == "button":
            return FieldType.CLICK_ONLY

        if tag_name == "a":
            return None

        if tag_name == "input" and input_type:
            return INPUT_TYPE_TO_FIELD_TYPE.get(input_type)

        if category == "text_input":
            return FieldType.TEXT

        return None

    def _group_radio_buttons(
        self,
        radios: list[dict[str, Any]],
    ) -> list[RadioButtonGroup]:
        """
        Group radio buttons by their name attribute.

        Args:
            radios: List of raw radio button element dicts

        Returns:
            List of RadioButtonGroup with grouped options

        """
        groups: dict[str, list[DiscoveredElement]] = {}

        for raw in radios:
            name = raw.get("name")
            if not name:
                name = "__unnamed__"

            if name not in groups:
                groups[name] = []

            discovered = self._create_discovered_element(raw=raw)
            groups[name].append(discovered)

        result: list[RadioButtonGroup] = []
        for group_name, options in groups.items():
            suggested_pattern = f"input[name='{group_name}']" if group_name != "__unnamed__" else "input[type='radio']"
            result.append(
                RadioButtonGroup(
                    group_name=group_name,
                    options=options,
                    suggested_selector_pattern=suggested_pattern,
                )
            )

        return result

    async def _discover_iframes(
        self,
        page: Page,
        iframe_infos: list[dict[str, Any]],
    ) -> list[IframeDiscovery]:
        """
        Discover iframes and their internal elements.

        Args:
            page: Playwright page instance
            iframe_infos: List of iframe info dicts from main page scan

        Returns:
            List of IframeDiscovery with elements found in each iframe

        """
        discoveries: list[IframeDiscovery] = []

        for iframe_info in iframe_infos:
            selector = iframe_info.get("selector")
            if not selector:
                continue

            try:
                frame_locator = page.frame_locator(selector)
                frame = frame_locator.owner

                frame_count = await frame.count()
                if frame_count == 0:
                    logger.info(f"Iframe not found: selector='{selector}'")
                    continue

                frame_element = (
                    page.frame(name=iframe_info.get("name") or "") or page.frames[1] if len(page.frames) > 1 else None
                )
                if not frame_element:
                    logger.info(f"Could not access iframe frame: selector='{selector}'")
                    continue

                raw_elements = await frame_element.evaluate(
                    """
                    () => {
                        const results = [];

                        function getVisibility(el) {
                            const rect = el.getBoundingClientRect();
                            const style = window.getComputedStyle(el);
                            const isVisible = rect.width > 0 && rect.height > 0 &&
                                              style.visibility !== 'hidden' &&
                                              style.display !== 'none';
                            if (!isVisible) return 'hidden';
                            return 'visible';
                        }

                        function findLabelText(el) {
                            if (el.id) {
                                const label = document.querySelector(`label[for="${el.id}"]`);
                                if (label) return label.textContent?.trim() || null;
                            }
                            return null;
                        }

                        function getElementInfo(el, category) {
                            const rect = el.getBoundingClientRect();
                            return {
                                category: category,
                                tagName: el.tagName.toLowerCase(),
                                id: el.id || null,
                                name: el.getAttribute('name') || null,
                                type: el.getAttribute('type') || null,
                                dataCy: el.getAttribute('data-cy') || null,
                                dataTestid: el.getAttribute('data-testid') || null,
                                dataQa: el.getAttribute('data-qa') || null,
                                placeholder: el.getAttribute('placeholder') || null,
                                ariaLabel: el.getAttribute('aria-label') || null,
                                labelText: findLabelText(el),
                                textContent: el.textContent?.trim().substring(0, 100) || null,
                                visibility: getVisibility(el),
                                boundingBox: { x: rect.x, y: rect.y, width: rect.width, height: rect.height }
                            };
                        }

                        document.querySelectorAll('input, textarea, select, button').forEach(el => {
                            results.push(getElementInfo(el, 'iframe_element'));
                        });

                        return results;
                    }
                    """
                )

                elements = [self._create_discovered_element(raw=raw) for raw in raw_elements]

                discoveries.append(
                    IframeDiscovery(
                        iframe_selector=selector,
                        iframe_src=iframe_info.get("src"),
                        iframe_name=iframe_info.get("name"),
                        elements=elements,
                    )
                )

                logger.info(f"Discovered {len(elements)} elements in iframe: selector='{selector}'")

            except (PlaywrightError, PlaywrightTimeoutError) as e:
                logger.warning(f"Failed to explore iframe: selector='{selector}' error='{e}'")
                continue

        return discoveries
