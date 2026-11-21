from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.models import (
    CollectionRun,
    PriceAlert,
    PriceHistory,
    Product,
    Retailer,
    RetailerProduct,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)) -> dict[str, object]:
    product_count = db.scalar(select(func.count(Product.id))) or 0
    retailer_count = db.scalar(select(func.count(Retailer.id)).where(Retailer.active.is_(True))) or 0
    active_offers = db.scalar(select(func.count(RetailerProduct.id))) or 0
    avg_price = db.scalar(select(func.avg(RetailerProduct.current_price))) or Decimal(0)

    recent_price_drops = db.scalar(
        select(func.count(PriceAlert.id)).where(
            PriceAlert.alert_type == "price_drop",
            PriceAlert.status == "active",
        )
    ) or 0

    out_of_stock = db.scalar(
        select(func.count(distinct(RetailerProduct.product_id))).where(
            RetailerProduct.stock_status == "out_of_stock"
        )
    ) or 0

    active_alerts = db.scalar(
        select(func.count(PriceAlert.id)).where(PriceAlert.status == "active")
    ) or 0

    latest_run = db.scalar(
        select(func.max(CollectionRun.finished_at)).where(CollectionRun.status == "completed")
    )

    # 1. 30-Day Price Movement Trends
    thirty_days_ago = datetime.now(UTC) - timedelta(days=30)
    history_records = db.execute(
        select(
            func.date(PriceHistory.observed_at).label("day"),
            func.avg(PriceHistory.observed_price).label("avg_price"),
            func.min(PriceHistory.observed_price).label("min_price"),
            func.max(PriceHistory.observed_price).label("max_price"),
        )
        .where(PriceHistory.observed_at >= thirty_days_ago)
        .group_by(func.date(PriceHistory.observed_at))
        .order_by(func.date(PriceHistory.observed_at))
    ).all()

    price_trends = [
        {
            "date": str(row[0]),
            "avg_price": round(float(row[1]), 2) if row[1] else 0.0,
            "min_price": round(float(row[2]), 2) if row[2] else 0.0,
            "max_price": round(float(row[3]), 2) if row[3] else 0.0,
        }
        for row in history_records
    ]

    # Fallback if no history yet
    if not price_trends:
        today = datetime.now(UTC)
        base_dec = Decimal(str(avg_price))
        price_trends = [
            {
                "date": (today - timedelta(days=i)).strftime("%Y-%m-%d"),
                "avg_price": float(round(base_dec, 2)),
                "min_price": float(round(base_dec * Decimal("0.85"), 2)),
                "max_price": float(round(base_dec * Decimal("1.15"), 2)),
            }
            for i in range(14, -1, -1)
        ]

    # 2. Category Distribution
    cat_records = db.execute(
        select(
            Product.category,
            func.count(Product.id).label("product_count"),
            func.avg(RetailerProduct.current_price).label("avg_price"),
        )
        .join(RetailerProduct, RetailerProduct.product_id == Product.id, isouter=True)
        .group_by(Product.category)
        .order_by(func.count(Product.id).desc())
    ).all()

    category_distribution = [
        {
            "category": row[0] or "General",
            "product_count": row[1],
            "avg_price": round(float(row[2]), 2) if row[2] else 0.0,
        }
        for row in cat_records
    ]

    # 3. Retailer Share & Comparison
    ret_records = db.execute(
        select(
            Retailer.name,
            func.count(RetailerProduct.id).label("offer_count"),
            func.avg(RetailerProduct.current_price).label("avg_price"),
        )
        .join(RetailerProduct, RetailerProduct.retailer_id == Retailer.id, isouter=True)
        .where(Retailer.active.is_(True))
        .group_by(Retailer.name)
    ).all()

    retailer_summary = [
        {
            "retailer": row[0],
            "offer_count": row[1],
            "avg_price": round(float(row[2]), 2) if row[2] else 0.0,
        }
        for row in ret_records
    ]

    return {
        "monitored_products": product_count,
        "active_retailers": retailer_count,
        "active_offers": active_offers,
        "average_product_price": round(float(avg_price), 2),
        "recent_price_drops": recent_price_drops,
        "out_of_stock_products": out_of_stock,
        "active_alerts": active_alerts,
        "last_successful_collection": latest_run.isoformat() if latest_run else None,
        "price_trends": price_trends,
        "category_distribution": category_distribution,
        "retailer_summary": retailer_summary,
    }
