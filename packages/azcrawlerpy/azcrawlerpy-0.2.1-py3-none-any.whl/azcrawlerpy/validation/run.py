"""Print field validation status for all validation schemas."""
# uv run python -m azcrawlerpy.validation.run

from . import (
    Base,
    ConfigToCrawl,
    CrawlerToData,
    CrawlToProxy,
    DataToCustomerDatabase,
    DataToDatabase,
    InputToConfig,
    InputToCrawl,
    InputToCrawler,
    InputToData,
    InputToProxy,
    InputToRequest,
    ProxyToCrawler,
    RequestToConfig,
)

SCHEMAS: list[type[Base]] = [
    InputToRequest,
    RequestToConfig,
    InputToConfig,
    ConfigToCrawl,
    InputToCrawl,
    CrawlToProxy,
    InputToProxy,
    ProxyToCrawler,
    InputToCrawler,
    CrawlerToData,
    InputToData,
    DataToDatabase,
    DataToCustomerDatabase,
]


def print_validation_status() -> None:
    for schema in SCHEMAS:
        print(f"\n=== {schema.__name__} ===")
        status = schema.get_field_validation_status()
        for field_name, field_status in status.items():
            print(f"  {field_name}: {field_status}")


if __name__ == "__main__":
    print_validation_status()
