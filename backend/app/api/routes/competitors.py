from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics.pricing import calculate_percentage_difference
from app.db.session import SessionLocal
from app.models.models import Product, Retailer, RetailerProduct

router = APIRouter(prefix="/competitors", tags=["competitors"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/comparison")
def competitor_comparison(
    reference_retailer: int,
    category: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    ref_retailer = db.get(Retailer, reference_retailer)
    if not ref_retailer:
        return {
            "reference_retailer": None,
            "items": [],
            "total": 0,
            "summary": {
                "total_comparisons": 0,
                "competitor_cheaper_count": 0,
                "reference_cheaper_count": 0,
                "same_price_count": 0,
            },
        }

    # Fetch reference retailer's offers
    ref_stmt = (
        select(RetailerProduct, Product)
        .join(Product, Product.id == RetailerProduct.product_id)
        .where(RetailerProduct.retailer_id == reference_retailer)
    )
    if category:
        ref_stmt = ref_stmt.where(Product.category == category)

    ref_rows = db.execute(ref_stmt).all()
    ref_map = {prod.id: (rp, prod) for rp, prod in ref_rows}
    matched_product_ids = list(ref_map.keys())

    if not matched_product_ids:
        return {
            "reference_retailer": ref_retailer.name,
            "items": [],
            "total": 0,
            "summary": {
                "total_comparisons": 0,
                "competitor_cheaper_count": 0,
                "reference_cheaper_count": 0,
                "same_price_count": 0,
            },
        }

    # Fetch competitor offers for the same products
    comp_stmt = (
        select(RetailerProduct, Retailer.name.label("retailer_name"))
        .join(Retailer, Retailer.id == RetailerProduct.retailer_id)
        .where(
            RetailerProduct.product_id.in_(matched_product_ids),
            RetailerProduct.retailer_id != reference_retailer,
        )
    )
    comp_rows = db.execute(comp_stmt).all()

    all_comparisons = []
    cheaper_count = 0
    more_expensive_count = 0
    same_count = 0

    for comp_rp, comp_retailer_name in comp_rows:
        ref_rp, prod = ref_map[comp_rp.product_id]
        ref_price = ref_rp.current_price
        comp_price = comp_rp.current_price

        abs_diff = abs(comp_price - ref_price)
        pct_diff = calculate_percentage_difference(ref_price, comp_price)
        is_cheaper = comp_price < ref_price

        if comp_price < ref_price:
            cheaper_count += 1
        elif comp_price > ref_price:
            more_expensive_count += 1
        else:
            same_count += 1

        all_comparisons.append({
            "product_id": prod.id,
            "product_name": prod.canonical_name,
            "category": prod.category,
            "brand": prod.brand,
            "reference_retailer": ref_retailer.name,
            "reference_price": float(ref_price),
            "reference_stock": ref_rp.stock_status,
            "competitor_retailer": comp_retailer_name,
            "competitor_price": float(comp_price),
            "competitor_stock": comp_rp.stock_status,
            "absolute_difference": float(abs_diff),
            "percentage_difference": float(pct_diff),
            "cheaper_competitor": is_cheaper,
        })

    paginated_items = all_comparisons[offset : offset + limit]

    return {
        "reference_retailer": ref_retailer.name,
        "items": paginated_items,
        "total": len(all_comparisons),
        "limit": limit,
        "offset": offset,
        "summary": {
            "total_comparisons": len(all_comparisons),
            "competitor_cheaper_count": cheaper_count,
            "reference_cheaper_count": more_expensive_count,
            "same_price_count": same_count,
        },
    }
