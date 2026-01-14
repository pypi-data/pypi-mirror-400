"""
Validation handler for request validation in handler chain.

Adds validation context (timestamps, validated attributes) to requests
and logs field validation status. Actual validation is handled by Pydantic
via Annotated types (NonEmptyStr, NonEmptyDict, JsonStr) defined in the
validation.base module.
"""

import datetime
import logging
from typing import Any

from pydantic import BaseModel

from .base import BaseHandler


class ValidationHandler(BaseHandler):
    """
    Handler that adds validation metadata to request context.

    Records validation timestamps and attribute lists in the context dict.
    Logs field validation status for debugging.
    """

    def __init__(self, logger: logging.Logger) -> None:
        """
        Initialize the validation handler.

        Args:
            logger: Logger instance for validation status output

        """
        super().__init__()
        self._logger = logger
        self._request_name: str = "Basic"
        self._display_name: str = "ValidationHandler"

    async def handle(self, request: BaseModel, context: dict[str, Any] | None = None) -> Any:
        if request and self._request_name == "Basic":
            self._request_name = getattr(request, "name", request.__class__.__name__)
        if self._request_name not in self._display_name:
            self._display_name = f"ValidationHandler{self._request_name}"
        if context is None:
            context = {}

        validated_attrs: list[str] = list(type(request).model_fields.keys())

        context[f"{self._request_name}_validation_passed"] = True
        context[f"{self._request_name}_validated_at"] = datetime.datetime.now(datetime.UTC).isoformat()
        context[f"{self._request_name}_validated_attributes"] = validated_attrs

        self._log_field_validation_status(request=request)

        self._logger.info(f"{self._display_name}: Request validation successful")
        return await super().handle(request=request, context=context)

    def _log_field_validation_status(self, request: BaseModel) -> None:
        """Log validation status for all fields on the request model."""
        request_class = type(request)
        if not hasattr(request_class, "get_field_validation_status"):
            return

        status_map = request_class.get_field_validation_status()
        self._logger.info(f"{self._display_name}: Field validation status:")
        for field_name, status in status_map.items():
            self._logger.info(f"  {field_name}: {status}")

    def __repr__(self) -> str:
        next_handler_name = type(self._next_handler).__name__ if self._next_handler else "None"
        return f"{self._display_name}(next_handler={next_handler_name})"
