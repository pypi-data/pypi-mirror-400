"""
Custom exceptions for the crawler framework.

All exceptions include context about the step and selector where the error occurred
to enable effective debugging. Supports AI agent diagnostics when debug mode enabled.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from .diagnostics import PageDiagnostics


class CrawlerError(Exception):
    """Base exception for all crawler framework errors."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.diagnostics: PageDiagnostics | None = None

    def with_diagnostics(self, diagnostics: PageDiagnostics) -> Self:
        """Attach diagnostics and return self for chaining."""
        self.diagnostics = diagnostics
        return self

    def to_dict(self) -> dict[str, Any]:
        """Serialize exception for JSON output."""
        return {
            "error_type": self.__class__.__name__,
            "message": str(self),
            "diagnostics": self.diagnostics.to_dict() if self.diagnostics else None,
        }

    def __str__(self) -> str:
        """Return message with diagnostics if available."""
        base_message = super().__str__()
        if self.diagnostics:
            return base_message + self.diagnostics.format_for_exception()
        return base_message


class FieldNotFoundError(CrawlerError):
    """Raised when a form field cannot be located on the page."""

    def __init__(self, selector: str, step_name: str, field_type: str) -> None:
        self.selector = selector
        self.step_name = step_name
        self.field_type = field_type
        message = f"Field not found: selector='{selector}' type='{field_type}' in step='{step_name}'"
        super().__init__(message)


class NavigationError(CrawlerError):
    """Raised when navigation between form steps fails."""

    def __init__(self, step_name: str, action_type: str, selector: str, reason: str) -> None:
        self.step_name = step_name
        self.action_type = action_type
        self.selector = selector
        self.reason = reason
        message = f"Navigation failed: action='{action_type}' selector='{selector}' in step='{step_name}': {reason}"
        super().__init__(message)


class CrawlerTimeoutError(CrawlerError):
    """Raised when waiting for an element or condition times out."""

    def __init__(self, selector: str, step_name: str, timeout_ms: int) -> None:
        self.selector = selector
        self.step_name = step_name
        self.timeout_ms = timeout_ms
        message = f"Timeout waiting for selector='{selector}' in step='{step_name}' after {timeout_ms}ms"
        super().__init__(message)


class InvalidInstructionError(CrawlerError):
    """Raised when the instruction JSON is invalid or malformed."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        message = f"Invalid instruction: {reason}"
        super().__init__(message)


class MissingDataError(CrawlerError):
    """Raised when required input data is missing for a field."""

    def __init__(self, data_key: str, step_name: str) -> None:
        self.data_key = data_key
        self.step_name = step_name
        message = f"Missing required data: key='{data_key}' in step='{step_name}'"
        super().__init__(message)


class FieldInteractionError(CrawlerError):
    """Raised when interaction with a field fails."""

    def __init__(self, selector: str, step_name: str, field_type: str, reason: str) -> None:
        self.selector = selector
        self.step_name = step_name
        self.field_type = field_type
        self.reason = reason
        message = f"Field interaction failed: selector='{selector}' type='{field_type}' in step='{step_name}': {reason}"
        super().__init__(message)


class IframeNotFoundError(CrawlerError):
    """Raised when an iframe cannot be located."""

    def __init__(self, iframe_selector: str, step_name: str) -> None:
        self.iframe_selector = iframe_selector
        self.step_name = step_name
        message = f"Iframe not found: selector='{iframe_selector}' in step='{step_name}'"
        super().__init__(message)


class UnsupportedFieldTypeError(CrawlerError):
    """Raised when an unsupported field type is encountered."""

    def __init__(self, field_type: str, step_name: str) -> None:
        self.field_type = field_type
        self.step_name = step_name
        message = f"Unsupported field type: '{field_type}' in step='{step_name}'"
        super().__init__(message)


class UnsupportedActionTypeError(CrawlerError):
    """Raised when an unsupported action type is encountered."""

    def __init__(self, action_type: str, step_name: str) -> None:
        self.action_type = action_type
        self.step_name = step_name
        message = f"Unsupported action type: '{action_type}' in step='{step_name}'"
        super().__init__(message)


class DataExtractionError(CrawlerError):
    """Raised when data extraction from the final page fails."""

    def __init__(self, field_name: str, selector: str, reason: str) -> None:
        self.field_name = field_name
        self.selector = selector
        self.reason = reason
        message = f"Data extraction failed: field='{field_name}' selector='{selector}': {reason}"
        super().__init__(message)
