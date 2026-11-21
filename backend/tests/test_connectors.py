from __future__ import annotations

from decimal import Decimal

from app.connectors.base import BaseConnector, ExtractedRecord
from app.connectors.demo_catalog import DemoCatalogConnector


def test_demo_catalog_connector() -> None:
    connector = DemoCatalogConnector(seed=123, item_count=25)
    records = list(connector.extract())
    assert len(records) == 25

    record = records[0]
    assert isinstance(record, ExtractedRecord)
    assert record.title
    assert record.brand
    assert record.category
    assert record.current_price > Decimal(0)
    assert record.source == "demo_catalog"
    assert connector.validate_record(record) is True


def test_base_connector_validation() -> None:
    connector = BaseConnector()
    valid_record = ExtractedRecord(
        title="Valid Product",
        brand="Brand",
        model_number=None,
        sku=None,
        gtin=None,
        category="Tech",
        current_price=Decimal("99.99"),
        original_price=None,
        currency="USD",
        availability="in_stock",
        retailer="Store",
        product_url=None,
        extracted_at=None,  # type: ignore
        source="test",
    )
    assert connector.validate_record(valid_record) is True

    invalid_record = ExtractedRecord(
        title="",  # missing title
        brand="Brand",
        model_number=None,
        sku=None,
        gtin=None,
        category="Tech",
        current_price=Decimal("-10.00"),  # negative price
        original_price=None,
        currency="USD",
        availability="in_stock",
        retailer="Store",
        product_url=None,
        extracted_at=None,  # type: ignore
        source="test",
    )
    assert connector.validate_record(invalid_record) is False
