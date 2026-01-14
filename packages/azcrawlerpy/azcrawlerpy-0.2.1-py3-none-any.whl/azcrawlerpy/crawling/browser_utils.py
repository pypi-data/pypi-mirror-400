"""
Browser utility functions for the crawler framework.

Shared browser-related utilities like cookie consent handling.
"""

from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from .config import (
    COOKIE_ACCEPT_BUTTON_TIMEOUT_MS,
    COOKIE_BANNER_SETTLE_DELAY_MS,
    COOKIE_BANNER_VISIBLE_TIMEOUT_MS,
    COOKIE_POST_CONSENT_DELAY_MS,
)
from .models import CookieConsentConfig
from .utils import setup_logger

logger = setup_logger(__name__)


async def handle_cookie_consent(page: Page, config: CookieConsentConfig) -> None:
    """
    Handle cookie consent banner using configured selectors or shadow DOM.

    Args:
        page: Playwright page instance
        config: Cookie consent configuration

    """
    logger.info(f"Checking for cookie consent banner: selector='{config.banner_selector}'")

    banner_settle_delay = (
        config.banner_settle_delay_ms if config.banner_settle_delay_ms is not None else COOKIE_BANNER_SETTLE_DELAY_MS
    )
    banner_visible_timeout = (
        config.banner_visible_timeout_ms
        if config.banner_visible_timeout_ms is not None
        else COOKIE_BANNER_VISIBLE_TIMEOUT_MS
    )
    accept_button_timeout = (
        config.accept_button_timeout_ms
        if config.accept_button_timeout_ms is not None
        else COOKIE_ACCEPT_BUTTON_TIMEOUT_MS
    )
    post_consent_delay = (
        config.post_consent_delay_ms if config.post_consent_delay_ms is not None else COOKIE_POST_CONSENT_DELAY_MS
    )

    await page.wait_for_timeout(banner_settle_delay)

    try:
        banner = page.locator(config.banner_selector)
        banner_count = await banner.count()
        if banner_count == 0:
            logger.info("No cookie consent banner found in DOM")
            return

        try:
            await banner.wait_for(state="visible", timeout=banner_visible_timeout)
            logger.info("Cookie consent banner visible")
        except PlaywrightTimeoutError:
            logger.info("Cookie consent banner in DOM but not visible, attempting to handle anyway")

        if config.shadow_host_selector and config.accept_button_texts:
            await _handle_shadow_dom_consent(page=page, config=config)
        elif config.accept_selector:
            accept_button = page.locator(config.accept_selector)
            await accept_button.wait_for(state="visible", timeout=accept_button_timeout)
            await accept_button.click()
            logger.info(f"Clicked accept button: selector='{config.accept_selector}'")

        await page.wait_for_timeout(post_consent_delay)
        logger.info("Cookie consent handling completed")
    except PlaywrightTimeoutError as e:
        logger.info(f"Cookie consent handling skipped: {e}")


async def _handle_shadow_dom_consent(page: Page, config: CookieConsentConfig) -> None:
    """
    Handle cookie consent in shadow DOM by evaluating JavaScript.

    Attempts to click an accept button inside the shadow root. Falls back to
    removing the banner element if no matching button is found.

    Args:
        page: Playwright page instance
        config: Cookie consent config with shadow_host_selector and accept_button_texts

    """
    accept_texts = config.accept_button_texts
    shadow_selector = config.shadow_host_selector
    banner_selector = config.banner_selector

    result = await page.evaluate(
        """
        ([shadowSelector, acceptTexts, bannerSelector]) => {
            const host = document.querySelector(shadowSelector);
            if (!host) return { status: 'no_host' };

            const shadowRoot = host.shadowRoot;
            if (!shadowRoot) return { status: 'no_shadow_root' };

            const buttons = shadowRoot.querySelectorAll('button');
            for (const btn of buttons) {
                const text = btn.textContent?.toLowerCase() || '';
                for (const acceptText of acceptTexts) {
                    if (text.includes(acceptText.toLowerCase())) {
                        btn.click();
                        return { status: 'clicked', button: text.substring(0, 30) };
                    }
                }
            }

            // If no button found, remove the banner to prevent blocking
            const banner = document.querySelector(bannerSelector);
            if (banner) {
                banner.remove();
                return { status: 'removed_banner' };
            }

            return { status: 'no_accept_button' };
        }
        """,
        [shadow_selector, accept_texts, banner_selector],
    )

    logger.info(f"Shadow DOM cookie consent result: {result}")
