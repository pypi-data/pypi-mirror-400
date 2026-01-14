"""
Diagnostic utilities for AI agent debugging.

Captures structured page state information when errors occur,
enabling AI agents to understand failures and suggest fixes.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from playwright.async_api import Page

from .utils import setup_logger

logger = setup_logger(__name__)


@dataclass
class SelectorInfo:
    """
    Information about a discovered selector on a page.

    Used for diagnostic output when a selector fails to match.
    """

    selector: str
    tag: str
    element_type: str | None
    text_content: str | None


@dataclass
class PageDiagnostics:
    """
    Structured page state for AI debugging.

    Contains all relevant page information needed to diagnose
    why a selector failed and suggest alternatives.
    """

    url: str
    title: str
    timestamp: str
    failed_selector: str | None
    step_name: str | None

    available_data_cy_selectors: list[SelectorInfo] = field(default_factory=list)
    visible_buttons: list[str] = field(default_factory=list)
    visible_inputs: list[str] = field(default_factory=list)
    suggested_selectors: list[str] = field(default_factory=list)

    html_snippet: str | None = None
    screenshot_path: Path | None = None

    console_errors: list[str] = field(default_factory=list)
    console_warnings: list[str] = field(default_factory=list)
    network_failed_requests: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "url": self.url,
            "title": self.title,
            "timestamp": self.timestamp,
            "failed_selector": self.failed_selector,
            "step_name": self.step_name,
            "available_data_cy_selectors": [
                {
                    "selector": s.selector,
                    "tag": s.tag,
                    "type": s.element_type,
                    "text": s.text_content[:50] if s.text_content else None,
                }
                for s in self.available_data_cy_selectors
            ],
            "visible_buttons": self.visible_buttons,
            "visible_inputs": self.visible_inputs,
            "suggested_selectors": self.suggested_selectors,
            "html_snippet": self.html_snippet,
            "screenshot_path": str(self.screenshot_path) if self.screenshot_path else None,
            "console_errors": self.console_errors,
            "console_warnings": self.console_warnings,
            "network_failed_requests": self.network_failed_requests,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    def format_for_exception(self) -> str:
        """Format diagnostics as a human-readable string for exception messages."""
        lines = [
            "",
            "=== AI DEBUG INFO ===",
            f"Page URL: {self.url}",
            f"Page Title: {self.title}",
            "",
        ]

        if self.available_data_cy_selectors:
            lines.append("Available data-cy selectors on this page:")
            for s in self.available_data_cy_selectors[:15]:
                type_info = f"[type={s.element_type}]" if s.element_type else ""
                lines.append(f"  - {s.selector} ({s.tag}{type_info})")
            if len(self.available_data_cy_selectors) > 15:
                lines.append(f"  ... and {len(self.available_data_cy_selectors) - 15} more")
            lines.append("")

        if self.visible_buttons:
            lines.append("Visible buttons:")
            for btn in self.visible_buttons[:10]:
                lines.append(f"  - {btn}")
            lines.append("")

        if self.visible_inputs:
            lines.append("Visible input fields:")
            for inp in self.visible_inputs[:10]:
                lines.append(f"  - {inp}")
            lines.append("")

        if self.suggested_selectors:
            lines.append("Suggested fix - try one of these selectors:")
            for s in self.suggested_selectors:
                lines.append(f"  - [data-cy='{s}']")
            lines.append("")

        if self.console_errors:
            lines.append("Console errors:")
            for err in self.console_errors[:5]:
                lines.append(f"  - {err[:100]}")
            lines.append("")

        if self.network_failed_requests:
            lines.append("Failed network requests:")
            for req in self.network_failed_requests[:5]:
                lines.append(f"  - {req.get('method', 'GET')} {req.get('url', '')[:80]}")
            lines.append("")

        if self.screenshot_path:
            lines.append(f"Screenshot saved: {self.screenshot_path}")

        lines.append("=====================")
        return "\n".join(lines)


@dataclass
class CrawlContext:
    """
    Context passed through crawl operations for diagnostics.

    Accumulates console messages and failed network requests during crawl.
    """

    output_dir: Path | None
    debug_enabled: bool
    console_messages: list[dict[str, Any]] = field(default_factory=list)
    failed_requests: list[dict[str, Any]] = field(default_factory=list)


def find_similar_selectors(
    failed_selector: str,
    available_selectors: list[str],
    threshold: float = 0.4,
) -> list[str]:
    """
    Find selectors similar to the failed one using sequence matching.

    Args:
        failed_selector: The selector that failed to find an element
        available_selectors: List of available selector values (without data-cy prefix)
        threshold: Minimum similarity ratio to include (0.0-1.0)

    Returns:
        List of similar selectors, sorted by similarity (most similar first)

    """
    failed_clean = _extract_data_cy_value(failed_selector)
    if not failed_clean:
        return []

    similarities: list[tuple[str, float]] = []
    for sel in available_selectors:
        ratio = SequenceMatcher(None, failed_clean.lower(), sel.lower()).ratio()
        if ratio >= threshold:
            similarities.append((sel, ratio))

    similarities.sort(key=lambda x: x[1], reverse=True)
    return [s[0] for s in similarities[:5]]


def _extract_data_cy_value(selector: str) -> str | None:
    """
    Extract the data-cy attribute value from a selector string.

    Args:
        selector: CSS selector string possibly containing data-cy attribute

    Returns:
        The data-cy value if found, otherwise the original selector

    """
    if "data-cy=" in selector:
        start = selector.find("data-cy=") + 9
        end_char = selector[start - 1]
        if end_char in ("'", '"'):
            end = selector.find(end_char, start)
            if end > start:
                return selector[start:end]
    return selector


async def capture_page_diagnostics(
    page: Page,
    context: CrawlContext,
    failed_selector: str | None,
    step_name: str | None,
    label: str,
) -> PageDiagnostics:
    """
    Capture comprehensive page diagnostics for AI debugging.

    Args:
        page: Playwright page instance
        context: Crawl context with console/network data
        failed_selector: The selector that failed (if applicable)
        step_name: Current step name
        label: Label for the screenshot file

    Returns:
        PageDiagnostics with captured page state

    """
    timestamp = datetime.now().isoformat(timespec="seconds")

    url = page.url
    title = await page.title()

    data_cy_selectors = await _capture_data_cy_selectors(page)
    visible_buttons = await _capture_visible_buttons(page)
    visible_inputs = await _capture_visible_inputs(page)

    suggested = []
    if failed_selector:
        available_names = [s.selector for s in data_cy_selectors]
        suggested = find_similar_selectors(
            failed_selector=failed_selector,
            available_selectors=available_names,
        )

    html_snippet = await _capture_html_snippet(page=page, selector=failed_selector)

    screenshot_path = None
    if context.debug_enabled and context.output_dir is not None:
        screenshot_path = context.output_dir / f"error_{label}.png"
        try:
            await page.screenshot(path=str(screenshot_path), full_page=True)
            logger.info(f"Diagnostic screenshot saved: path='{screenshot_path}'")
        except (OSError, TimeoutError) as e:
            logger.warning(f"Failed to capture diagnostic screenshot: {e}")
            screenshot_path = None

    console_errors = [msg["text"] for msg in context.console_messages if msg.get("type") == "error"]
    console_warnings = [msg["text"] for msg in context.console_messages if msg.get("type") == "warning"]

    return PageDiagnostics(
        url=url,
        title=title,
        timestamp=timestamp,
        failed_selector=failed_selector,
        step_name=step_name,
        available_data_cy_selectors=data_cy_selectors,
        visible_buttons=visible_buttons,
        visible_inputs=visible_inputs,
        suggested_selectors=suggested,
        html_snippet=html_snippet,
        screenshot_path=screenshot_path,
        console_errors=console_errors,
        console_warnings=console_warnings,
        network_failed_requests=context.failed_requests,
    )


async def _capture_data_cy_selectors(page: Page) -> list[SelectorInfo]:
    """
    Capture all elements with data-cy attributes on the page.

    Args:
        page: Playwright page instance

    Returns:
        List of SelectorInfo for each data-cy element found

    """
    items = await page.evaluate(
        """
        () => {
            const elements = document.querySelectorAll('[data-cy]');
            return Array.from(elements).map(el => ({
                selector: el.getAttribute('data-cy'),
                tag: el.tagName.toLowerCase(),
                type: el.getAttribute('type'),
                text: el.textContent?.trim().substring(0, 100) || null
            }));
        }
        """
    )
    return [
        SelectorInfo(
            selector=item["selector"],
            tag=item["tag"],
            element_type=item["type"],
            text_content=item["text"],
        )
        for item in items
    ]


async def _capture_visible_buttons(page: Page) -> list[str]:
    """
    Capture text of visible buttons on the page.

    Args:
        page: Playwright page instance

    Returns:
        List of button descriptions with data-cy and text content

    """
    return await page.evaluate(
        """
        () => {
            const buttons = document.querySelectorAll('button:not([hidden])');
            return Array.from(buttons)
                .filter(btn => {
                    const rect = btn.getBoundingClientRect();
                    return rect.width > 0 && rect.height > 0;
                })
                .map(btn => {
                    const dataCy = btn.getAttribute('data-cy');
                    const text = btn.textContent?.trim().substring(0, 50) || '';
                    return dataCy ? `[data-cy='${dataCy}'] "${text}"` : `"${text}"`;
                })
                .slice(0, 20);
        }
        """
    )


async def _capture_visible_inputs(page: Page) -> list[str]:
    """
    Capture information about visible input fields on the page.

    Args:
        page: Playwright page instance

    Returns:
        List of input field descriptions with selectors and types

    """
    return await page.evaluate(
        """
        () => {
            const inputs = document.querySelectorAll('input:not([type="hidden"]), textarea, select');
            return Array.from(inputs)
                .filter(inp => {
                    const rect = inp.getBoundingClientRect();
                    return rect.width > 0 && rect.height > 0;
                })
                .map(inp => {
                    const dataCy = inp.getAttribute('data-cy');
                    const name = inp.getAttribute('name');
                    const type = inp.getAttribute('type') || inp.tagName.toLowerCase();
                    const placeholder = inp.getAttribute('placeholder') || '';

                    let identifier = dataCy ? `[data-cy='${dataCy}']` :
                                     name ? `[name='${name}']` :
                                     inp.tagName.toLowerCase();
                    return `${identifier} (${type}) ${placeholder}`.trim();
                })
                .slice(0, 20);
        }
        """
    )


async def _capture_html_snippet(page: Page, selector: str | None) -> str | None:
    """
    Capture a relevant HTML snippet around the failed selector area.

    Args:
        page: Playwright page instance
        selector: The failed selector to find context for

    Returns:
        HTML snippet from the main form/content area, or None

    """
    if not selector:
        return None

    try:
        return await page.evaluate(
            """
            (selector) => {
                // Try to find elements with similar data-cy values
                const allDataCy = document.querySelectorAll('[data-cy]');
                if (allDataCy.length === 0) return null;

                // Get the main form or content area
                const form = document.querySelector('form') || document.querySelector('main') || document.body;
                if (!form) return null;

                // Return a truncated version of the form HTML
                const html = form.outerHTML;
                return html.length > 5000 ? html.substring(0, 5000) + '...' : html;
            }
            """,
            selector,
        )
    except (OSError, TimeoutError):
        return None


def write_diagnostic_json(
    output_dir: Path,
    error: Exception,
    diagnostics: "PageDiagnostics",
) -> Path:
    """
    Write diagnostic information to a JSON file.

    Args:
        output_dir: Directory to write the file
        error: The exception that occurred
        diagnostics: Captured page diagnostics

    Returns:
        Path to the written JSON file

    """
    output_path = output_dir / "error_diagnostics.json"

    data = {
        "timestamp": diagnostics.timestamp,
        "success": False,
        "error": {
            "type": type(error).__name__,
            "message": str(error),
            "step_name": diagnostics.step_name,
            "failed_selector": diagnostics.failed_selector,
        },
        "diagnostics": diagnostics.to_dict(),
    }

    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"Diagnostic JSON saved: path='{output_path}'")

    return output_path
