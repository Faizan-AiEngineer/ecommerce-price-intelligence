from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.security import require_api_key
from app.db.session import SessionLocal
from app.models.models import PriceAlert, Product, Retailer, RetailerProduct
from app.schemas.schemas import AlertUpdate

router = APIRouter(prefix="/alerts", tags=["alerts"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("")
async def list_alerts(
    status: str | None = Query(default=None),
    alert_type: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
):
    stmt = (
        select(
            PriceAlert,
            Product.canonical_name.label("product_name"),
            Product.category.label("category"),
            Retailer.name.label("retailer_name"),
        )
        .join(Product, Product.id == PriceAlert.product_id)
        .join(RetailerProduct, RetailerProduct.id == PriceAlert.retailer_product_id, isouter=True)
        .join(Retailer, Retailer.id == RetailerProduct.retailer_id, isouter=True)
    )

    if status:
        stmt = stmt.where(PriceAlert.status == status)
    if alert_type:
        stmt = stmt.where(PriceAlert.alert_type == alert_type)

    stmt = stmt.order_by(desc(PriceAlert.created_at)).limit(limit).offset(offset)
    records = db.execute(stmt).all()

    items = []
    for alert, prod_name, cat, ret_name in records:
        # Formulate human-readable description
        message = ""
        if alert.alert_type == "price_drop":
            pct = ""
            if alert.previous_value and alert.previous_value > 0 and alert.current_value:
                drop_pct = abs(round(((alert.current_value - alert.previous_value) / alert.previous_value) * 100, 1))
                pct = f" (-{drop_pct}%)"
            message = f"Price dropped from ${float(alert.previous_value or 0):.2f} to ${float(alert.current_value or 0):.2f}{pct}"
        elif alert.alert_type == "price_increase":
            message = f"Price increased from ${float(alert.previous_value or 0):.2f} to ${float(alert.current_value or 0):.2f}"
        elif alert.alert_type == "competitor_undercut":
            message = f"{ret_name or 'Competitor'} undercutting reference price by ${float(alert.threshold or 0):.2f}"
        elif alert.alert_type == "out_of_stock":
            message = f"Product went out of stock at {ret_name or 'retailer'}"
        elif alert.alert_type == "back_in_stock":
            message = f"Product returned to stock at {ret_name or 'retailer'}"

        items.append({
            "id": alert.id,
            "product_id": alert.product_id,
            "product_name": prod_name,
            "category": cat,
            "retailer_product_id": alert.retailer_product_id,
            "retailer_name": ret_name,
            "alert_type": alert.alert_type,
            "message": message,
            "previous_value": float(alert.previous_value) if alert.previous_value is not None else None,
            "current_value": float(alert.current_value) if alert.current_value is not None else None,
            "threshold": float(alert.threshold) if alert.threshold is not None else None,
            "status": alert.status,
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
        })

    return {"items": items, "total": len(items)}


@router.patch("/{alert_id}")
async def patch_alert(
    alert_id: int,
    payload: AlertUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(require_api_key),
):
    alert = db.get(PriceAlert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = payload.status
    db.commit()
    return {"id": alert.id, "status": alert.status}
