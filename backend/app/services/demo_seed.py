from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.alerts.engine import generate_alerts
from app.analytics.pricing import normalize_price
from app.models.models import (
    CollectionRun,
    DataSource,
    PriceHistory,
    Product,
    Retailer,
    RetailerProduct,
)

logger = logging.getLogger(__name__)


def generate_demo_data(product_count: int = 500, history_days: int = 90) -> dict[str, list[dict[str, object]]]:
    categories = ["Laptops", "Smartphones", "Audio", "Wearables", "Home Office", "Accessories"]
    brands = ["Apex", "NorthPeak", "NovaCore", "Helio", "Summit", "Orbitel"]
    retailers = [
        {"name": "MarketHub", "website": "https://markethub.example", "currency": "USD", "country": "US"},
        {"name": "ValueCart", "website": "https://valuecart.example", "currency": "USD", "country": "US"},
        {"name": "PrimeSelect", "website": "https://primeselect.example", "currency": "USD", "country": "US"},
    ]

    products: list[dict[str, object]] = []
    for idx in range(product_count):
        category = categories[idx % len(categories)]
        brand = brands[idx % len(brands)]
        model = f"{brand}-{category[:3].upper()}-{idx + 1:04d}"
        products.append({
            "canonical_name": f"{brand} {category.removesuffix('s')} {model}",
            "brand": brand,
            "category": category,
            "model_number": model,
            "gtin": f"978{idx + 1:012d}",
            "description": f"High performance {brand} product in the {category} category.",
        })

    offer_rows: list[dict[str, object]] = []
    history_rows: list[dict[str, object]] = []
    for idx, product in enumerate(products):
        base = 45 + (idx * 1.7 % 800)
        for retailer_index, retailer in enumerate(retailers):
            current_price = Decimal(str(round(base + retailer_index * 12 + (idx % 9) * 3.5, 2)))
            original_price = current_price * Decimal("1.12")
            offer_rows.append({
                "retailer_name": retailer["name"],
                "product_name": product["canonical_name"],
                "product_id": idx,
                "current_price": normalize_price(current_price),
                "original_price": normalize_price(original_price),
                "stock_status": "in_stock" if (idx + retailer_index) % 7 != 0 else "out_of_stock",
                "retailer_sku": f"SKU-{idx + 1:06d}-{retailer_index + 1}",
                "product_url": f"https://example.com/products/{idx + 1}?ref={retailer['name'].lower()}",
            })
            for day_offset in range(history_days):
                observed = datetime.now(UTC) - timedelta(days=history_days - 1 - day_offset)
                daily_delta = Decimal(str((day_offset % 7) * 1.5 + retailer_index * 2))
                observed_price = current_price + (Decimal(idx % 10) * Decimal("0.35")) + (Decimal(day_offset % 5) * Decimal("0.7")) - daily_delta
                observed_price = max(Decimal("15.00"), observed_price)
                history_rows.append({
                    "retailer_name": retailer["name"],
                    "product_name": product["canonical_name"],
                    "observed_price": normalize_price(observed_price),
                    "original_price": normalize_price(original_price),
                    "stock_status": "in_stock" if (day_offset + idx + retailer_index) % 9 else "out_of_stock",
                    "observed_at": observed,
                })

    return {"retailers": retailers, "products": products, "offers": offer_rows, "history": history_rows}


def seed_demo_database(db: Session, product_count: int = 500, history_days: int = 90) -> dict[str, int]:
    logger.info("Generating demo data (products=%d, history_days=%d)...", product_count, history_days)
    dataset = generate_demo_data(product_count=product_count, history_days=history_days)

    # 1. Retailers
    retailer_rows = [Retailer(**r) for r in dataset["retailers"]]
    db.add_all(retailer_rows)
    db.commit()

    # 2. Products
    product_rows = [Product(**p) for p in dataset["products"]]
    db.add_all(product_rows)
    db.commit()

    retailer_by_name = {r.name: r for r in db.query(Retailer).all()}
    product_by_name = {p.canonical_name: p for p in db.query(Product).all()}

    # 3. Data Source & Collection Run
    source = DataSource(
        name="demo_catalog",
        source_type="demo",
        configuration={"seed": 42, "product_count": product_count},
        enabled=True,
    )
    db.add(source)
    db.commit()

    run = CollectionRun(
        source_id=source.id,
        status="completed",
        records_extracted=product_count,
        records_loaded=product_count,
        finished_at=datetime.now(UTC),
    )
    db.add(run)
    db.commit()

    # 4. Offers (RetailerProduct)
    offer_objs = []
    for offer in dataset["offers"]:
        prod = product_by_name.get(str(offer["product_name"]))
        ret = retailer_by_name.get(str(offer["retailer_name"]))
        if prod and ret:
            offer_objs.append(RetailerProduct(
                retailer_id=ret.id,
                product_id=prod.id,
                retailer_sku=str(offer["retailer_sku"]),
                product_url=str(offer["product_url"]),
                retailer_product_name=str(offer["product_name"]),
                current_price=offer["current_price"],  # type: ignore
                currency=ret.currency,
                stock_status=str(offer["stock_status"]),
            ))
    db.add_all(offer_objs)
    db.commit()

    # 5. Price History (batch insert in chunks)
    retailer_products = db.query(RetailerProduct).all()
    rp_by_key = {(rp.retailer_id, rp.product_id): rp for rp in retailer_products}

    history_objs = []
    chunk_size = 5000
    history_count = 0

    for entry in dataset["history"]:
        prod = product_by_name.get(str(entry["product_name"]))
        ret = retailer_by_name.get(str(entry["retailer_name"]))
        if not prod or not ret:
            continue
        rp = rp_by_key.get((ret.id, prod.id))
        if not rp:
            continue

        history_objs.append(PriceHistory(
            retailer_product_id=rp.id,
            observed_price=entry["observed_price"],  # type: ignore
            original_price=entry["original_price"],  # type: ignore
            currency=ret.currency,
            stock_status=str(entry["stock_status"]),
            observed_at=entry["observed_at"],  # type: ignore
            collection_run_id=run.id,
        ))
        history_count += 1

        if len(history_objs) >= chunk_size:
            db.add_all(history_objs)
            db.commit()
            history_objs = []

    if history_objs:
        db.add_all(history_objs)
        db.commit()

    # 6. Generate Realistic Alerts
    alerts_created = generate_alerts(db, price_change_threshold_pct=Decimal("4.0"))
    logger.info("Demo database seeded successfully with %d alerts.", alerts_created)

    return {
        "retailers": len(retailer_rows),
        "products": len(product_rows),
        "offers": len(offer_objs),
        "history": history_count,
        "alerts": alerts_created,
    }
