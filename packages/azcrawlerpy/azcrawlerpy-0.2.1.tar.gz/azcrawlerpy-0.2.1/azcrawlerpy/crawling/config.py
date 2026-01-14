"""
Centralized configuration constants for the crawler framework.

All timeout values, delay constants, and control variables are defined here.
"""

# Browser Configuration
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
DEFAULT_VIEWPORT_WIDTH = 1920
DEFAULT_VIEWPORT_HEIGHT = 1080

# Cookie Consent Timeouts (milliseconds)
COOKIE_BANNER_SETTLE_DELAY_MS = 2000
COOKIE_BANNER_VISIBLE_TIMEOUT_MS = 3000
COOKIE_ACCEPT_BUTTON_TIMEOUT_MS = 5000
COOKIE_POST_CONSENT_DELAY_MS = 1000

# Action Timeouts (milliseconds)
ACTION_PRE_DELAY_MS = 2000
ACTION_POST_DELAY_MS = 5000
ACTION_ELEMENT_ATTACHED_TIMEOUT_MS = 30000
ACTION_WAIT_TIMEOUT_MS = 30000

# Field Handler Timeouts (milliseconds)
FIELD_VISIBLE_TIMEOUT_MS = 10000
FIELD_POST_CLICK_DELAY_MS = 1000
FIELD_TYPE_DELAY_MS = 50
FIELD_WAIT_AFTER_TYPE_MS = 1000
FIELD_OPTION_VISIBLE_TIMEOUT_MS = 10000
FIELD_WAIT_AFTER_CLICK_MS = 500

# Field Handler Delays (seconds) - used with asyncio.sleep
COMBOBOX_PRE_TYPE_DELAY_SECONDS = 0.3
COMBOBOX_POST_CLEAR_DELAY_SECONDS = 0.2
COMBOBOX_POST_ENTER_DELAY_SECONDS = 0.3

# Discovery Timeouts (milliseconds)
DISCOVERY_PAGE_LOAD_TIMEOUT_MS = 30000

# CSS Selector Special Characters that need escaping
CSS_SELECTOR_ESCAPE_CHARS = ":[]().#>+~="

# Characters that need escaping in CSS attribute values
CSS_ATTRIBUTE_VALUE_ESCAPE_CHARS = "\"'\\[]"
