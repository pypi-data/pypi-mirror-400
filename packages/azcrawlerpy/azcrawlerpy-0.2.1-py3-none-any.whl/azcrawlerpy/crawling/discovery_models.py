"""
Pydantic models for element discovery output.

All models use strict validation with no defaults - missing required fields
will cause immediate validation errors.
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from .models import FieldType


class ElementVisibility(str, Enum):
    """Element visibility status on the page."""

    VISIBLE = "visible"
    HIDDEN = "hidden"
    OFF_SCREEN = "off_screen"


class DiscoveredElement(BaseModel):
    """A single discovered interactive element."""

    model_config = ConfigDict(extra="forbid")

    tag_name: str = Field(description="HTML tag name (e.g., input, button, select)")
    suggested_field_type: FieldType | None = Field(description="Mapped FieldType enum value")
    selector: str = Field(description="Suggested CSS selector (prefers unique attributes)")
    alternative_selectors: list[str] = Field(description="Alternative selector strategies")

    element_id: str | None = Field(description="Element id attribute")
    name: str | None = Field(description="Element name attribute")
    input_type: str | None = Field(description="Input type attribute (text, email, etc.)")

    data_cy: str | None = Field(description="data-cy attribute value")
    data_testid: str | None = Field(description="data-testid attribute value")
    data_qa: str | None = Field(description="data-qa attribute value")

    label_text: str | None = Field(description="Associated label text")
    placeholder: str | None = Field(description="Placeholder attribute")
    aria_label: str | None = Field(description="ARIA label attribute")
    text_content: str | None = Field(description="Element text content (truncated to 100 chars)")

    visibility: ElementVisibility = Field(description="Element visibility status")
    bounding_box: dict[str, float] | None = Field(description="Position: x, y, width, height")

    option_count: int | None = Field(description="Number of options (for select elements)")
    options_preview: list[str] | None = Field(description="First few option texts")

    group_name: str | None = Field(description="Name attribute for grouping radios")
    href: str | None = Field(description="href attribute for links")


class RadioButtonGroup(BaseModel):
    """A group of radio buttons with the same name."""

    model_config = ConfigDict(extra="forbid")

    group_name: str = Field(description="Shared name attribute")
    options: list[DiscoveredElement] = Field(description="Radio buttons in this group")
    suggested_selector_pattern: str = Field(description="Selector pattern for the group")


class IframeDiscovery(BaseModel):
    """Discovered iframe with its internal elements."""

    model_config = ConfigDict(extra="forbid")

    iframe_selector: str = Field(description="CSS selector for the iframe")
    iframe_src: str | None = Field(description="iframe src attribute")
    iframe_name: str | None = Field(description="iframe name attribute")
    elements: list[DiscoveredElement] = Field(description="Elements discovered inside iframe")


class PageDiscoveryReport(BaseModel):
    """Complete discovery report for a web page."""

    model_config = ConfigDict(extra="forbid")

    url: str = Field(description="Page URL")
    title: str = Field(description="Page title")
    timestamp: str = Field(description="Discovery timestamp ISO format")

    text_inputs: list[DiscoveredElement] = Field(description="Text, email, password, tel, url inputs")
    textareas: list[DiscoveredElement] = Field(description="Textarea elements")
    selects: list[DiscoveredElement] = Field(description="Select/dropdown elements")
    radio_groups: list[RadioButtonGroup] = Field(description="Radio button groups")
    checkboxes: list[DiscoveredElement] = Field(description="Checkbox elements")
    buttons: list[DiscoveredElement] = Field(description="Button and submit elements")
    links: list[DiscoveredElement] = Field(description="Anchor elements with href")
    date_inputs: list[DiscoveredElement] = Field(description="Date and datetime inputs")
    file_inputs: list[DiscoveredElement] = Field(description="File upload inputs")
    sliders: list[DiscoveredElement] = Field(description="Range/slider inputs")
    custom_components: list[DiscoveredElement] = Field(
        description="Elements with data-cy/testid/qa not captured elsewhere"
    )
    iframes: list[IframeDiscovery] = Field(description="Iframes with their elements")

    total_elements: int = Field(description="Total interactive elements found")
    screenshot_path: str | None = Field(description="Path to screenshot if captured")
