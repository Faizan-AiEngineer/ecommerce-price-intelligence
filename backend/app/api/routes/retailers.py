from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.models import Retailer, RetailerProduct

router = APIRouter(prefix="/retailers", tags=["retailers"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class RetailerCreate(BaseModel):
    name: str
    website: str
    currency: str = "USD"
    country: str = "US"
    active: bool = True


@router.get("")
async def list_retailers(db: Session = Depends(get_db)):
    retailers = db.execute(select(Retailer).order_by(Retailer.id)).scalars().all()

    # Aggregate offer counts and avg prices
    stats = db.execute(
        select(
            RetailerProduct.retailer_id,
            func.count(RetailerProduct.id).label("offer_count"),
            func.avg(RetailerProduct.current_price).label("avg_price"),
            func.min(RetailerProduct.current_price).label("min_price"),
            func.max(RetailerProduct.current_price).label("max_price"),
        ).group_by(RetailerProduct.retailer_id)
    ).all()

    stats_map = {
        row[0]: {
            "offer_count": row[1],
            "avg_price": round(float(row[2]), 2) if row[2] else 0.0,
            "min_price": round(float(row[3]), 2) if row[3] else 0.0,
            "max_price": round(float(row[4]), 2) if row[4] else 0.0,
        }
        for row in stats
    }

    return {
        "items": [
            {
                "id": r.id,
                "name": r.name,
                "website": r.website,
                "currency": r.currency,
                "country": r.country,
                "active": r.active,
                "offer_count": stats_map.get(r.id, {}).get("offer_count", 0),
                "avg_price": stats_map.get(r.id, {}).get("avg_price", 0.0),
                "min_price": stats_map.get(r.id, {}).get("min_price", 0.0),
                "max_price": stats_map.get(r.id, {}).get("max_price", 0.0),
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in retailers
        ]
    }


@router.post("")
async def create_retailer(payload: RetailerCreate, db: Session = Depends(get_db)):
    existing = db.execute(select(Retailer).where(Retailer.name == payload.name)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Retailer with this name already exists")

    retailer = Retailer(
        name=payload.name,
        website=payload.website,
        currency=payload.currency,
        country=payload.country,
        active=payload.active,
    )
    db.add(retailer)
    db.commit()
    db.refresh(retailer)
    return {"id": retailer.id, "name": retailer.name, "created_at": retailer.created_at.isoformat()}
