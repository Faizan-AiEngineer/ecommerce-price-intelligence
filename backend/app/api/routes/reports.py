from __future__ import annotations

import io

import pandas as pd
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.models import Product, Retailer, RetailerProduct

router = APIRouter(prefix="/reports", tags=["reports"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/export")
async def export_reports(
    file_format: str = Query(default="csv", pattern=r"^(csv|xlsx)$"),
    category: str | None = None,
    db: Session = Depends(get_db),
):
    stmt = (
        select(
            Product.canonical_name,
            Product.brand,
            Product.category,
            Product.model_number,
            Product.gtin,
            Retailer.name.label("retailer"),
            RetailerProduct.current_price,
            RetailerProduct.currency,
            RetailerProduct.stock_status,
            RetailerProduct.last_checked_at,
        )
        .join(RetailerProduct, RetailerProduct.product_id == Product.id)
        .join(Retailer, Retailer.id == RetailerProduct.retailer_id)
    )

    if category:
        stmt = stmt.where(Product.category == category)

    records = db.execute(stmt).all()

    rows = [
        {
            "Product": r[0],
            "Brand": r[1],
            "Category": r[2],
            "Model Number": r[3] or "",
            "GTIN": r[4] or "",
            "Retailer": r[5],
            "Current Price": float(r[6]),
            "Currency": r[7],
            "Stock Status": r[8],
            "Last Checked": r[9].strftime("%Y-%m-%d %H:%M:%S") if r[9] else "",
        }
        for r in records
    ]

    df = pd.DataFrame(rows)

    if file_format == "csv":
        output = io.StringIO()
        df.to_csv(output, index=False)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode("utf-8")),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=competitor_price_intelligence.csv"},
        )

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Price Intelligence")
    excel_buffer.seek(0)
    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=competitor_price_intelligence.xlsx"},
    )
