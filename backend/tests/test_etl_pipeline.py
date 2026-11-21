from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import Base
from app.models.models import PriceHistory, Product, Retailer, RetailerProduct
from app.services.etl import (
    deduplicate_records,
    load_validated_records,
    normalize_record,
)


@pytest.fixture
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def test_normalize_record() -> None:
    raw = {
        "title": "  Sony WH-1000XM5 Headphones  ",
        "brand": "Sony",
        "current_price": "$349.99",
        "original_price": "$399.99",
        "currency": "usd",
        "availability": "In Stock",
        "retailer": "BestBuy",
    }
    normalized = normalize_record(raw)
    assert normalized["canonical_name"] == "Sony WH-1000XM5 Headphones"
    assert normalized["current_price"] == Decimal("349.99")
    assert normalized["original_price"] == Decimal("399.99")
    assert normalized["currency"] == "USD"
    assert normalized["availability"] == "in_stock"
    assert normalized["retailer"] == "BestBuy"


def test_deduplicate_records() -> None:
    records = [
        {"canonical_name": "Product A", "retailer": "Retailer 1", "current_price": Decimal("100.00")},
        {"canonical_name": "Product A", "retailer": "Retailer 1", "current_price": Decimal("100.00")},
        {"canonical_name": "Product B", "retailer": "Retailer 1", "current_price": Decimal("100.00")},
    ]
    unique = deduplicate_records(records)
    assert len(unique) == 2


def test_etl_idempotency_and_loading(db_session: Session) -> None:
    now = datetime(2026, 11, 13, 12, 0, 0, tzinfo=UTC)
    records = [
        {
            "canonical_name": "UltraBook Pro 15",
            "brand": "TechCorp",
            "model_number": "UB-15",
            "gtin": "1234567890123",
            "category": "Laptops",
            "current_price": Decimal("899.99"),
            "original_price": Decimal("999.99"),
            "currency": "USD",
            "availability": "in_stock",
            "retailer": "MarketHub",
            "product_url": "https://example.com/ub15",
            "extracted_at": now,
        }
    ]

    # First load
    count1 = load_validated_records(db_session, records)
    assert count1 == 1

    # Verify entities
    product = db_session.query(Product).filter_by(gtin="1234567890123").first()
    assert product is not None
    assert product.canonical_name == "UltraBook Pro 15"

    retailer = db_session.query(Retailer).filter_by(name="MarketHub").first()
    assert retailer is not None

    offer = db_session.query(RetailerProduct).filter_by(product_id=product.id, retailer_id=retailer.id).first()
    assert offer is not None
    assert offer.current_price == Decimal("899.99")

    history_count1 = db_session.query(PriceHistory).count()
    assert history_count1 == 1

    # Second load with identical observation timestamp & price (Idempotency test)
    count2 = load_validated_records(db_session, records)
    assert count2 == 0  # Duplicate observation not re-inserted
    assert db_session.query(PriceHistory).count() == 1
