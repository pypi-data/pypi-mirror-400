"""
Base validation schema with shared logic.

Provides Annotated types for common validation patterns and a base model
class with field validation introspection capabilities.
"""

import json
from typing import Annotated, Any

from pydantic import AfterValidator, BaseModel, ConfigDict


def _validate_non_empty_string(v: str) -> str:
    """Validate that string is not empty or whitespace-only."""
    if not v or not v.strip():
        msg = "Field cannot be empty or whitespace only"
        raise ValueError(msg)
    return v


def _validate_non_empty_dict(v: dict[str, Any]) -> dict[str, Any]:
    """Validate that dictionary is not empty."""
    if not v:
        msg = "Dict field cannot be empty"
        raise ValueError(msg)
    return v


def _validate_json_string(v: str) -> str:
    """Validate that string contains valid JSON representing an object."""
    if not v or not v.strip():
        msg = "Field cannot be empty or whitespace only"
        raise ValueError(msg)
    try:
        parsed = json.loads(v)
        if not isinstance(parsed, dict):
            msg = "JSON string must represent an object/dict"
            raise ValueError(msg)
    except json.JSONDecodeError as e:
        msg = f"Field must contain valid JSON: {e}"
        raise ValueError(msg) from e
    return v


NonEmptyStr = Annotated[str, AfterValidator(_validate_non_empty_string)]
NonEmptyDict = Annotated[dict[str, Any], AfterValidator(_validate_non_empty_dict)]
JsonStr = Annotated[str, AfterValidator(_validate_json_string)]


class Base(BaseModel):
    """
    Base validation schema with shared configuration and introspection.

    Provides strict validation mode and methods to inspect which fields
    have validators and where those validators are defined in the class hierarchy.
    """

    model_config = ConfigDict(strict=True)

    @property
    def name(self) -> str:
        """Return the class name as the model name."""
        return self.__class__.__name__

    @classmethod
    def get_field_validation_status(cls) -> dict[str, str]:
        """
        Get validation status for all fields.

        Returns:
            Dict mapping field names to validation status:
            - 'validated' for fields validated in the current class
            - 'validated(ParentClassName)' for fields validated in a parent class
            - 'unvalidated' for fields without validators

        """
        all_fields = set(cls.model_fields.keys())
        field_validation_source: dict[str, str | None] = {}

        for field_name in all_fields:
            field_validation_source[field_name] = cls._find_validation_source(field_name=field_name)

        result: dict[str, str] = {}
        for field_name in sorted(all_fields):
            source = field_validation_source[field_name]
            if source is None:
                result[field_name] = "unvalidated"
            elif source == cls.__name__:
                result[field_name] = "validated"
            else:
                result[field_name] = f"validated({source})"

        return result

    @classmethod
    def _find_validation_source(cls, field_name: str) -> str | None:
        """
        Find which class in the MRO first defines validation for a field.

        Args:
            field_name: Name of the field to check

        Returns:
            Class name where validation is defined, or None if unvalidated

        """
        source_class: str | None = None

        for klass in reversed(cls.__mro__):
            if not hasattr(klass, "__annotations__"):
                continue

            if field_name not in klass.__annotations__:
                continue

            if hasattr(klass, "__pydantic_decorators__"):
                decorators = klass.__pydantic_decorators__
                for validator_info in decorators.field_validators.values():
                    if field_name in validator_info.info.fields:
                        source_class = klass.__name__
                        break

            if hasattr(klass, "model_fields") and field_name in klass.model_fields:
                field_info = klass.model_fields[field_name]
                metadata = getattr(field_info, "metadata", None)
                if metadata:
                    for meta in metadata:
                        if isinstance(meta, AfterValidator):
                            source_class = klass.__name__
                            break

        return source_class
