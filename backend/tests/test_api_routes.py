from __future__ import annotations

from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.routes import competitors, dashboard, health, products
from app.db.session import Base
from app.models.models import PriceAlert, Product, Retailer, RetailerProduct


@pytest.fixture
def test_db() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    try:
        # Seed test data
        r1 = Retailer(name="MarketHub", website="https://markethub.example", currency="USD")
        r2 = Retailer(name="ValueCart", website="https://valuecart.example", currency="USD")
        p = Product(canonical_name="Apex Laptop 15", brand="Apex", category="Laptops", model_number="AX15", gtin="1234567890123")
        session.add_all([r1, r2, p])
        session.commit()

        rp1 = RetailerProduct(retailer_id=r1.id, product_id=p.id, current_price=Decimal("999.00"), stock_status="in_stock")
        rp2 = RetailerProduct(retailer_id=r2.id, product_id=p.id, current_price=Decimal("949.00"), stock_status="in_stock")
        alert = PriceAlert(product_id=p.id, retailer_product_id=rp2.id, alert_type="price_drop", previous_value=Decimal("999.00"), current_value=Decimal("949.00"), threshold=Decimal("5.0"), status="active")
        session.add_all([rp1, rp2, alert])
        session.commit()

        yield session
    finally:
        session.close()


def test_health_endpoint() -> None:
    res = health.health_check()
    assert res["status"] == "ok"
    assert res["service"] == "price-intelligence-api"


def test_dashboard_summary_endpoint(test_db: Session) -> None:
    summary = dashboard.dashboard_summary(db=test_db)
    assert summary["monitored_products"] == 1
    assert summary["active_retailers"] == 2
    assert summary["active_offers"] == 2
    assert summary["average_product_price"] > 0
    assert summary["active_alerts"] == 1
    assert len(summary["category_distribution"]) >= 1


def test_products_list_and_detail(test_db: Session) -> None:
    result = products.list_products(db=test_db)
    assert result["total"] == 1
    assert len(result["items"]) == 1
    item = result["items"][0]
    assert item["canonical_name"] == "Apex Laptop 15"
    assert item["offer_count"] == 2

    # Detail
    detail = products.get_product(product_id=item["id"], db=test_db)
    assert detail["canonical_name"] == "Apex Laptop 15"
    assert detail["lowest_price"] == 949.00
    assert len(detail["offers"]) == 2


def test_competitor_comparison_endpoint(test_db: Session) -> None:
    # Compare with reference retailer 1 (MarketHub)
    res = competitors.competitor_comparison(reference_retailer=1, db=test_db)
    assert res["reference_retailer"] == "MarketHub"
    assert len(res["items"]) == 1
    comp = res["items"][0]
    assert comp["competitor_retailer"] == "ValueCart"
    assert comp["competitor_price"] == 949.00
    assert comp["cheaper_competitor"] is True
    assert comp["absolute_difference"] == 50.00
