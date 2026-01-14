"""Validation schemas for request operations."""

from .base import Base, NonEmptyStr


class InputToRequest(Base):
    """Validation schema for request input data."""

    website_name: NonEmptyStr
    project_code: NonEmptyStr
    resource_group_environment: NonEmptyStr


class RequestToConfig(InputToRequest):
    """Validation schema for request-to-config operations."""

    customer: NonEmptyStr
    crawl_origin_tickets_storage_account_name: NonEmptyStr
    crawl_origin_data_full_cosmos_db_name: NonEmptyStr
    InputToRequest_validated_at: NonEmptyStr
