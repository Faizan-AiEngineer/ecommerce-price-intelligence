from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.models import PriceHistory, Product, Retailer, RetailerProduct

router = APIRouter(prefix="/products", tags=["products"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("")
def list_products(
    q: str | None = None,
    category: str | None = None,
    brand: str | None = None,
    retailer: str | None = None,
    stock: str | None = None,
    limit: int = 25,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    stmt = select(Product)
    count_stmt = select(func.count(Product.id))

    if q:
        search_filter = (
            Product.canonical_name.ilike(f"%{q}%")
            | Product.brand.ilike(f"%{q}%")
            | Product.model_number.ilike(f"%{q}%")
        )
        stmt = stmt.where(search_filter)
        count_stmt = count_stmt.where(search_filter)

    if category:
        stmt = stmt.where(Product.category == category)
        count_stmt = count_stmt.where(Product.category == category)

    if brand:
        stmt = stmt.where(Product.brand == brand)
        count_stmt = count_stmt.where(Product.brand == brand)

    total_count = db.scalar(count_stmt) or 0

    stmt = stmt.order_by(Product.id.asc()).limit(limit).offset(offset)
    products = db.execute(stmt).scalars().all()

    # Enrich products with offers data
    product_ids = [p.id for p in products]
    offers_by_product: dict[int, list[dict]] = {pid: [] for pid in product_ids}

    if product_ids:
        offers_query = (
            select(RetailerProduct, Retailer.name.label("retailer_name"))
            .join(Retailer, Retailer.id == RetailerProduct.retailer_id)
            .where(RetailerProduct.product_id.in_(product_ids))
        )
        offers_rows = db.execute(offers_query).all()
        for rp, r_name in offers_rows:
            offers_by_product[rp.product_id].append({
                "id": rp.id,
                "retailer_id": rp.retailer_id,
                "retailer_name": r_name,
                "retailer_sku": rp.retailer_sku,
                "product_url": rp.product_url,
                "current_price": float(rp.current_price),
                "currency": rp.currency,
                "stock_status": rp.stock_status,
                "last_checked_at": rp.last_checked_at.isoformat() if rp.last_checked_at else None,
            })

    items = []
    for p in products:
        p_offers = offers_by_product.get(p.id, [])
        prices = [o["current_price"] for o in p_offers]
        min_p = min(prices) if prices else 0.0
        max_p = max(prices) if prices else 0.0
        avg_p = sum(prices) / len(prices) if prices else 0.0
        in_stock_any = any(o["stock_status"] in ("in_stock", "limited") for o in p_offers)

        # Apply stock filter in memory if specified
        if stock == "in_stock" and not in_stock_any:
            continue
        if stock == "out_of_stock" and in_stock_any and p_offers:
            continue

        items.append({
            "id": p.id,
            "canonical_name": p.canonical_name,
            "brand": p.brand,
            "category": p.category,
            "model_number": p.model_number,
            "gtin": p.gtin,
            "description": p.description,
            "min_price": round(min_p, 2),
            "max_price": round(max_p, 2),
            "avg_price": round(avg_p, 2),
            "offer_count": len(p_offers),
            "stock_status": "in_stock" if in_stock_any else "out_of_stock",
            "offers": p_offers,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        })

    return {
        "items": items,
        "total": total_count,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    offers_query = (
        select(RetailerProduct, Retailer.name.label("retailer_name"), Retailer.website.label("retailer_website"))
        .join(Retailer, Retailer.id == RetailerProduct.retailer_id)
        .where(RetailerProduct.product_id == product_id)
    )
    offers_rows = db.execute(offers_query).all()

    offers = []
    prices = []
    for rp, r_name, r_site in offers_rows:
        price_flt = float(rp.current_price)
        prices.append(price_flt)
        offers.append({
            "id": rp.id,
            "retailer_id": rp.retailer_id,
            "retailer_name": r_name,
            "retailer_website": r_site,
            "retailer_sku": rp.retailer_sku,
            "product_url": rp.product_url,
            "current_price": price_flt,
            "currency": rp.currency,
            "stock_status": rp.stock_status,
            "last_checked_at": rp.last_checked_at.isoformat() if rp.last_checked_at else None,
        })

    min_price = min(prices) if prices else 0.0
    max_price = max(prices) if prices else 0.0
    cheapest_retailer = next((o["retailer_name"] for o in offers if o["current_price"] == min_price), None)

    return {
        "id": product.id,
        "canonical_name": product.canonical_name,
        "brand": product.brand,
        "category": product.category,
        "model_number": product.model_number,
        "gtin": product.gtin,
        "description": product.description,
        "lowest_price": min_price,
        "highest_price": max_price,
        "cheapest_retailer": cheapest_retailer,
        "offers": offers,
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
    }


@router.get("/{product_id}/price-history")
def get_price_history(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    query = (
        select(
            PriceHistory,
            Retailer.name.label("retailer_name"),
            RetailerProduct.retailer_id,
        )
        .join(RetailerProduct, RetailerProduct.id == PriceHistory.retailer_product_id)
        .join(Retailer, Retailer.id == RetailerProduct.retailer_id)
        .where(RetailerProduct.product_id == product_id)
        .order_by(PriceHistory.observed_at.asc())
    )
    records = db.execute(query).all()

    history = [
        {
            "id": ph.id,
            "retailer_product_id": ph.retailer_product_id,
            "retailer_id": r_id,
            "retailer_name": r_name,
            "observed_price": float(ph.observed_price),
            "original_price": float(ph.original_price) if ph.original_price else None,
            "stock_status": ph.stock_status,
            "observed_at": ph.observed_at.isoformat(),
        }
        for ph, r_name, r_id in records
    ]

    return {"product_id": product_id, "history": history}
