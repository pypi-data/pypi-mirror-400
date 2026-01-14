"""
Pydantic models for instruction and data validation.

All models use strict validation with no defaults - missing required fields
will cause immediate validation errors.
"""

from enum import Enum
from pathlib import Path
from typing import Annotated, Any

from pydantic import AfterValidator, BaseModel, ConfigDict, Field


def _validate_non_empty_selector(v: str) -> str:
    if not v or not v.strip():
        msg = "Selector cannot be empty or whitespace only"
        raise ValueError(msg)
    return v


NonEmptySelector = Annotated[str, AfterValidator(_validate_non_empty_selector)]


class DebugMode(str, Enum):
    """Debug screenshot modes."""

    NONE = "none"
    START = "start"
    END = "end"
    ALL = "all"


class FieldType(str, Enum):
    """Supported form field types."""

    TEXT = "text"
    TEXTAREA = "textarea"
    DROPDOWN = "dropdown"
    SELECT = "select"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    DATE = "date"
    SLIDER = "slider"
    FILE = "file"
    IFRAME_FIELD = "iframe_field"
    CLICK_ONLY = "click_only"
    COMBOBOX = "combobox"
    CLICK_SELECT = "click_select"


class ActionType(str, Enum):
    """Supported action types for navigation and interaction."""

    CLICK = "click"
    WAIT = "wait"
    WAIT_HIDDEN = "wait_hidden"
    SCROLL = "scroll"
    DELAY = "delay"
    CONDITIONAL = "conditional"


class FieldDefinition(BaseModel):
    """Definition of a single form field to interact with."""

    model_config = ConfigDict(extra="forbid")

    data_key: str | None = Field(
        default=None, description="Key in input_data dict to get the value from (optional for click_only)"
    )
    selector: NonEmptySelector = Field(description="CSS selector to locate the field")
    type: FieldType = Field(description="Type of the form field")
    format: str | None = Field(default=None, description="Format string for date fields")
    iframe_selector: str | None = Field(default=None, description="CSS selector for iframe if field is inside one")
    select_by: str | None = Field(
        default=None, description="How to select dropdown options: 'value', 'text', or 'index'"
    )
    option_selector: str | None = Field(
        default=None, description="CSS selector for combobox options (used with COMBOBOX type)"
    )
    type_delay_ms: int | None = Field(
        default=None, description="Delay between keystrokes in ms for slow typing (combobox/autocomplete)"
    )
    wait_after_type_ms: int | None = Field(
        default=None, description="Wait time in ms after typing before selecting option"
    )
    press_enter: bool | None = Field(
        default=None, description="Press Enter after selecting option (for some autocomplete fields)"
    )
    clear_before_type: bool | None = Field(
        default=None, description="Clear the field before typing (triple-click select all)"
    )
    field_visible_timeout_ms: int | None = Field(default=None, description="Timeout in ms for field visibility")
    post_click_delay_ms: int | None = Field(default=None, description="Wait time in ms after clicking field")
    option_visible_timeout_ms: int | None = Field(
        default=None, description="Timeout in ms for option visibility in dropdowns"
    )
    skip_verification: bool | None = Field(
        default=None, description="Skip value verification after filling (for fields that may disappear)"
    )
    force_click: bool | None = Field(
        default=None, description="Use force click to bypass element interception (for sticky toolbars, overlays)"
    )


class ActionDefinition(BaseModel):
    """Definition of an action to perform during navigation."""

    model_config = ConfigDict(extra="forbid")

    type: ActionType = Field(description="Type of action to perform")
    selector: str | None = Field(default=None, description="CSS selector for the action target")
    iframe_selector: str | None = Field(default=None, description="CSS selector for iframe if target is inside one")
    delay_ms: int | None = Field(default=None, description="Delay in milliseconds for delay action")
    condition: dict[str, Any] | None = Field(default=None, description="Condition for conditional action")
    actions: list["ActionDefinition"] | None = Field(default=None, description="Nested actions for conditional action")
    pre_action_delay_ms: int | None = Field(default=None, description="Wait time in ms before executing action")
    post_action_delay_ms: int | None = Field(default=None, description="Wait time in ms after executing action")


class StepExtractionDefinition(BaseModel):
    """Definition of data to extract during a step, with optional field interactions."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(description="Name for this extraction (used as key prefix in extracted_data)")
    selector: NonEmptySelector = Field(description="CSS selector to locate the value element")
    attribute: str | None = Field(default=None, description="Element attribute to extract, or None for text content")
    regex: str | None = Field(default=None, description="Optional regex pattern (uses first capture group if present)")
    wait_before_ms: int | None = Field(
        default=None, description="Wait time in ms before extraction (useful for post-field extraction where UI needs to update)"
    )
    click_before: str | None = Field(
        default=None, description="CSS selector to click before extracting (e.g., to switch tabs/options)"
    )
    force_click: bool = Field(
        default=True, description="Whether to use force click (bypasses visibility checks but may not trigger JS handlers)"
    )
    wait_after_click_ms: int | None = Field(
        default=None, description="Wait time in ms after clicking before extraction"
    )
    dismiss_modal_selector: str | None = Field(
        default=None, description="CSS selector to click after extraction to dismiss modal (e.g., close button)"
    )


class StepDefinition(BaseModel):
    """Definition of a single form step (page)."""

    model_config = ConfigDict(extra="forbid")

    name: NonEmptySelector = Field(description="Unique name for this step")
    wait_for: NonEmptySelector = Field(description="CSS selector or condition to wait for before interacting")
    fields: list[FieldDefinition] = Field(description="List of fields to fill in this step")
    next_action: ActionDefinition = Field(description="Action to perform to navigate to next step")
    timeout_ms: int = Field(description="Timeout in milliseconds for waiting")
    data_extraction: list[StepExtractionDefinition] | None = Field(
        default=None, description="Optional list of data to extract BEFORE field handling in this step"
    )
    post_field_extraction: list[StepExtractionDefinition] | None = Field(
        default=None, description="Optional list of data to extract AFTER field handling (useful for modal results)"
    )


class FinalPageDefinition(BaseModel):
    """Definition of the final result page."""

    model_config = ConfigDict(extra="forbid")

    wait_for: NonEmptySelector = Field(description="CSS selector to wait for on the final page")
    screenshot_selector: str | None = Field(
        default=None, description="CSS selector for element to screenshot, or None for full page"
    )
    timeout_ms: int = Field(description="Timeout in milliseconds for waiting")


class ExtractionFieldDefinition(BaseModel):
    """Definition of a single data extraction field."""

    model_config = ConfigDict(extra="forbid")

    selector: NonEmptySelector = Field(description="CSS selector to locate element(s)")
    attribute: str | None = Field(description="Element attribute to extract, or None for text content")
    regex: str | None = Field(description="Optional regex pattern (uses first capture group if present)")
    multiple: bool = Field(description="True for list of all matches, False for first match only")
    iframe_selector: str | None = Field(default=None, description="CSS selector for iframe if element is inside one")


class NestedOutputFormat(str, Enum):
    """Output formats for nested field assembly."""

    PAIRED_DICT = "paired_dict"
    OBJECT_LIST = "object_list"


class NestedFieldDefinition(BaseModel):
    """Definition of a nested field that combines multiple flat fields into a structured output."""

    model_config = ConfigDict(extra="forbid")

    output_format: NestedOutputFormat = Field(description="Output format: paired_dict or object_list")
    key_field: str | None = Field(
        default=None, description="Source field for dict keys (required for paired_dict format)"
    )
    value_field: str | None = Field(
        default=None, description="Source field for dict values (required for paired_dict format)"
    )
    fields: dict[str, str] | None = Field(
        default=None,
        description="Mapping of output field names to source fields (required for object_list format)",
    )


class DataExtractionConfig(BaseModel):
    """Configuration for extracting structured data from the final page."""

    model_config = ConfigDict(extra="forbid")

    fields: dict[str, ExtractionFieldDefinition] = Field(
        description="Dictionary mapping field names to their extraction definitions"
    )
    nested_fields: dict[str, NestedFieldDefinition] | None = Field(
        default=None,
        description="Optional nested field definitions that combine flat fields into structured outputs",
    )


class BrowserConfig(BaseModel):
    """Configuration for browser settings."""

    model_config = ConfigDict(extra="forbid")

    viewport_width: int = Field(description="Browser viewport width in pixels")
    viewport_height: int = Field(description="Browser viewport height in pixels")
    user_agent: str | None = Field(default=None, description="Custom user agent string")


class CookieConsentConfig(BaseModel):
    """Configuration for cookie consent banner handling."""

    model_config = ConfigDict(extra="forbid")

    banner_selector: NonEmptySelector = Field(description="CSS selector for the cookie consent banner")
    accept_selector: str | None = Field(
        default=None, description="CSS selector for the accept button (for regular banners)"
    )
    shadow_host_selector: str | None = Field(
        default=None, description="CSS selector for shadow DOM host (for Usercentrics etc.)"
    )
    accept_button_texts: list[str] | None = Field(
        default=None,
        description="Text patterns to match accept buttons in shadow DOM (e.g., ['akzeptieren', 'accept all'])",
    )
    banner_settle_delay_ms: int | None = Field(default=None, description="Wait time in ms before checking for banner")
    banner_visible_timeout_ms: int | None = Field(default=None, description="Timeout in ms for banner visibility")
    accept_button_timeout_ms: int | None = Field(default=None, description="Timeout in ms for accept button visibility")
    post_consent_delay_ms: int | None = Field(default=None, description="Wait time in ms after cookie handling")


class Instructions(BaseModel):
    """Complete instruction set for form crawling."""

    model_config = ConfigDict(extra="forbid")

    url: str = Field(description="Starting URL for the crawler")
    browser_config: BrowserConfig | None = Field(default=None, description="Optional browser configuration")
    steps: list[StepDefinition] = Field(description="Ordered list of form steps to process")
    final_page: FinalPageDefinition = Field(description="Configuration for the final result page")
    cookie_consent: CookieConsentConfig | None = Field(
        default=None, description="Optional cookie consent banner handling configuration"
    )
    data_extraction: DataExtractionConfig | None = Field(
        default=None, description="Optional configuration for extracting structured data from final page"
    )


class CrawlResult(BaseModel):
    """Result of a successful crawl operation with file output."""

    model_config = ConfigDict(extra="forbid")

    html_path: Path = Field(description="Path to saved HTML file")
    screenshot_path: Path = Field(description="Path to saved screenshot")
    final_url: str = Field(description="Final URL after all navigation")
    steps_completed: int = Field(description="Number of steps successfully completed")
    extracted_data: dict[str, Any] = Field(description="Extracted data from final page")


class InMemoryCrawlResult(BaseModel):
    """Result of a successful crawl operation returned in-memory without file output."""

    model_config = ConfigDict(extra="forbid")

    url: str = Field(description="Starting URL that was crawled")
    input_data: dict[str, Any] = Field(description="Input data used to fill form fields")
    instructions: dict[str, Any] = Field(description="Instructions used for crawling")
    screenshots: list[bytes] = Field(description="List of screenshot images as bytes")
    html: str = Field(description="Final page HTML content")
    final_url: str = Field(description="Final URL after all navigation")
    steps_completed: int = Field(description="Number of steps successfully completed")
    extracted_data: dict[str, Any] = Field(description="Extracted data from final page")

    def __repr__(self) -> str:
        def truncate(value: str, max_length: int = 50) -> str:
            if len(value) <= max_length:
                return value
            return value[: max_length - 3] + "..."

        def format_bytes(size: int) -> str:
            if size < 1024:
                return f"{size} B"
            if size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            return f"{size / (1024 * 1024):.1f} MB"

        def format_dict(data: dict[str, Any], max_keys: int = 3) -> str:
            keys = list(data.keys())
            if len(keys) <= max_keys:
                return str(keys)
            return f"{keys[:max_keys]} ... ({len(keys)} keys)"

        screenshot_info = f"{len(self.screenshots)} screenshots"
        if self.screenshots:
            total_size = sum(len(s) for s in self.screenshots)
            screenshot_info += f" ({format_bytes(total_size)})"

        rows = [
            ("url", truncate(self.url, max_length=60)),
            ("final_url", truncate(self.final_url, max_length=60)),
            ("steps_completed", str(self.steps_completed)),
            ("input_data", format_dict(self.input_data, max_keys=50)),
            ("instructions", format_dict(self.instructions, max_keys=50)),
            ("screenshots", screenshot_info),
            ("html", f"{len(self.html):,} chars"),
            ("extracted_data", format_dict(self.extracted_data)),
        ]

        label_width = max(len(row[0]) for row in rows)
        lines = ["InMemoryCrawlResult:"]
        lines.append("-" * (label_width + 65))
        for label, value in rows:
            lines.append(f"  {label:<{label_width}}  |  {value}")
        lines.append("-" * (label_width + 65))

        return "\n".join(lines)

    def __str__(self) -> str:
        return self.__repr__()
