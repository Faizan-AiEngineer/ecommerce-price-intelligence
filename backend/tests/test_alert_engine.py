from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.alerts.engine import generate_alerts
from app.db.session import Base
from app.models.models import (
    PriceAlert,
    PriceHistory,
    Product,
    Retailer,
    RetailerProduct,
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


def test_price_drop_and_undercut_alerts(db_session: Session) -> None:
    # Set up reference and competitor retailers
    ref_retailer = Retailer(name="MarketHub", website="https://markethub.example", currency="USD")
    comp_retailer = Retailer(name="ValueCart", website="https://valuecart.example", currency="USD")
    product = Product(canonical_name="SmartWatch Ultra", brand="Apex", category="Wearables")
    db_session.add_all([ref_retailer, comp_retailer, product])
    db_session.commit()

    # Reference offer at $200
    ref_offer = RetailerProduct(
        retailer_id=ref_retailer.id,
        product_id=product.id,
        current_price=Decimal("200.00"),
        stock_status="in_stock",
    )
    # Competitor offer at $180 (undercutting)
    comp_offer = RetailerProduct(
        retailer_id=comp_retailer.id,
        product_id=product.id,
        current_price=Decimal("180.00"),
        stock_status="in_stock",
    )
    db_session.add_all([ref_offer, comp_offer])
    db_session.commit()

    now = datetime.now(UTC)
    # Add history for competitor showing a price drop from $210 to $180 (14.2% drop)
    ph1 = PriceHistory(
        retailer_product_id=comp_offer.id,
        observed_price=Decimal("210.00"),
        stock_status="in_stock",
        observed_at=now - timedelta(days=2),
    )
    ph2 = PriceHistory(
        retailer_product_id=comp_offer.id,
        observed_price=Decimal("180.00"),
        stock_status="in_stock",
        observed_at=now - timedelta(days=1),
    )
    db_session.add_all([ph1, ph2])
    db_session.commit()

    # Generate alerts with 5% threshold
    alerts_created = generate_alerts(db_session, price_change_threshold_pct=Decimal("5.0"), reference_retailer_name="MarketHub")
    assert alerts_created >= 2  # Should create price_drop and competitor_undercut

    alerts = db_session.query(PriceAlert).all()
    alert_types = [a.alert_type for a in alerts]
    assert "price_drop" in alert_types
    assert "competitor_undercut" in alert_types

    # Deduplication test: running again should create 0 new alerts
    second_run_alerts = generate_alerts(db_session, price_change_threshold_pct=Decimal("5.0"), reference_retailer_name="MarketHub")
    assert second_run_alerts == 0
