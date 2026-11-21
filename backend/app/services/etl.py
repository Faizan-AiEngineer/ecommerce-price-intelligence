from __future__ import annotations

import logging
import re
from collections.abc import Iterable
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.alerts.engine import generate_alerts
from app.analytics.pricing import normalize_currency, normalize_price
from app.connectors.base import BaseConnector, ExtractedRecord
from app.models.models import (
    CollectionRun,
    DataSource,
    PriceHistory,
    Product,
    Retailer,
    RetailerProduct,
)

logger = logging.getLogger(__name__)


def clean_title(title: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", title.lower())
    return " ".join(cleaned.split())


def normalize_record(raw_record: dict[str, object] | ExtractedRecord) -> dict[str, object]:
    if isinstance(raw_record, ExtractedRecord):
        return {
            "canonical_name": raw_record.title.strip(),
            "brand": raw_record.brand.strip(),
            "model_number": (raw_record.model_number or "").strip() or None,
            "sku": (raw_record.sku or "").strip() or None,
            "gtin": (raw_record.gtin or "").strip() or None,
            "category": (raw_record.category or "General").strip(),
            "current_price": normalize_price(raw_record.current_price),
            "original_price": normalize_price(raw_record.original_price) if raw_record.original_price is not None else None,
            "currency": normalize_currency(raw_record.currency),
            "availability": (raw_record.availability or "in_stock").strip().lower().replace(" ", "_"),
            "retailer": raw_record.retailer.strip(),
            "product_url": (raw_record.product_url or "").strip() or None,
            "extracted_at": raw_record.extracted_at or datetime.now(UTC),
            "source": raw_record.source,
        }

    return {
        "canonical_name": str(raw_record.get("title", "")).strip(),
        "brand": str(raw_record.get("brand", "")).strip(),
        "model_number": str(raw_record.get("model_number") or "").strip() or None,
        "sku": str(raw_record.get("sku") or "").strip() or None,
        "gtin": str(raw_record.get("gtin") or "").strip() or None,
        "category": str(raw_record.get("category", "General")).strip() or "General",
        "current_price": normalize_price(raw_record.get("current_price", 0)),
        "original_price": normalize_price(raw_record.get("original_price")) if raw_record.get("original_price") is not None else None,
        "currency": normalize_currency(str(raw_record.get("currency") or "USD")),
        "availability": str(raw_record.get("availability", "in_stock")).strip().lower().replace(" ", "_") or "in_stock",
        "retailer": str(raw_record.get("retailer", "Unknown Retailer")).strip(),
        "product_url": str(raw_record.get("product_url") or "").strip() or None,
        "extracted_at": raw_record.get("extracted_at") or datetime.now(UTC),
        "source": str(raw_record.get("source", "manual")),
    }


def deduplicate_records(records: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    seen: set[tuple[str, str, str]] = set()
    unique: list[dict[str, object]] = []
    for record in records:
        key = (str(record["canonical_name"]), str(record["retailer"]), str(record["current_price"]))
        if key in seen:
            continue
        seen.add(key)
        unique.append(record)
    return unique


def find_matching_product(db: Session, record: dict[str, object]) -> Product | None:
    # 1. Exact GTIN match
    gtin = record.get("gtin")
    if gtin:
        product = db.execute(select(Product).where(Product.gtin == gtin)).scalar_one_or_none()
        if product:
            return product

    # 2. Exact Brand + Model match
    brand = record.get("brand")
    model = record.get("model_number")
    if brand and model:
        product = db.execute(
            select(Product).where(Product.brand == brand, Product.model_number == model)
        ).scalar_one_or_none()
        if product:
            return product

    # 3. Canonical name match
    canonical = record.get("canonical_name")
    if canonical:
        product = db.execute(
            select(Product).where(Product.canonical_name == canonical)
        ).scalar_one_or_none()
        if product:
            return product

    return None


def upsert_product(db: Session, record: dict[str, object]) -> Product:
    product = find_matching_product(db, record)
    if product is None:
        product = Product(
            canonical_name=str(record["canonical_name"]),
            brand=str(record.get("brand") or ""),
            category=str(record.get("category") or "General"),
            model_number=record.get("model_number"),  # type: ignore
            gtin=record.get("gtin"),  # type: ignore
            description=str(record.get("canonical_name") or ""),
        )
        db.add(product)
        db.flush()
    else:
        product.canonical_name = str(record["canonical_name"])
        if record.get("brand"):
            product.brand = str(record["brand"])
        if record.get("category") and record["category"] != "General":
            product.category = str(record["category"])
        if record.get("model_number"):
            product.model_number = str(record["model_number"])
        if record.get("gtin"):
            product.gtin = str(record["gtin"])
        db.flush()
    return product


def upsert_retailer(db: Session, name: str, currency: str = "USD") -> Retailer:
    retailer = db.execute(select(Retailer).where(Retailer.name == name)).scalar_one_or_none()
    if retailer is None:
        safe_domain = re.sub(r"[^a-zA-Z0-9]", "", name.lower())
        retailer = Retailer(
            name=name,
            website=f"https://{safe_domain}.example",
            currency=currency,
            country="US",
            active=True,
        )
        db.add(retailer)
        db.flush()
    return retailer


def upsert_offer(db: Session, product: Product, retailer: Retailer, record: dict[str, object]) -> RetailerProduct:
    offer = db.execute(
        select(RetailerProduct).where(
            RetailerProduct.product_id == product.id,
            RetailerProduct.retailer_id == retailer.id,
        )
    ).scalar_one_or_none()

    if offer is None:
        offer = RetailerProduct(
            retailer_id=retailer.id,
            product_id=product.id,
            retailer_sku=str(record.get("sku") or ""),
            product_url=str(record.get("product_url") or ""),
            retailer_product_name=str(record["canonical_name"]),
            current_price=record["current_price"],  # type: ignore
            currency=str(record.get("currency") or "USD"),
            stock_status=str(record.get("availability") or "in_stock"),
            last_checked_at=datetime.now(UTC),
        )
        db.add(offer)
        db.flush()
    else:
        offer.current_price = record["current_price"]  # type: ignore
        offer.stock_status = str(record.get("availability") or "in_stock")
        offer.last_checked_at = datetime.now(UTC)
        if record.get("product_url"):
            offer.product_url = str(record["product_url"])
        if record.get("sku"):
            offer.retailer_sku = str(record["sku"])
        db.flush()
    return offer


def load_validated_records(
    db: Session,
    records: Iterable[dict[str, object]],
    collection_run_id: int | None = None,
) -> int:
    inserted = 0
    for record in deduplicate_records(records):
        if not record.get("canonical_name"):
            continue
        if record["current_price"] < Decimal(0):  # type: ignore
            continue

        product = upsert_product(db, record)
        retailer = upsert_retailer(db, str(record["retailer"]), str(record.get("currency") or "USD"))
        offer = upsert_offer(db, product, retailer, record)

        # Idempotency check: don't insert duplicate observation for same offer, timestamp, and price
        existing_history = db.execute(
            select(PriceHistory).where(
                PriceHistory.retailer_product_id == offer.id,
                PriceHistory.observed_at == record["extracted_at"],
                PriceHistory.observed_price == record["current_price"],
            )
        ).scalar_one_or_none()

        if existing_history is None:
            db.add(PriceHistory(
                retailer_product_id=offer.id,
                observed_price=record["current_price"],  # type: ignore
                original_price=record.get("original_price"),  # type: ignore
                currency=str(record.get("currency") or "USD"),
                stock_status=str(record.get("availability") or "in_stock"),
                observed_at=record["extracted_at"],  # type: ignore
                collection_run_id=collection_run_id,
            ))
            inserted += 1

    db.commit()
    return inserted


def run_collection_pipeline(
    db: Session,
    connector: BaseConnector,
    source_id: int | None = None,
) -> CollectionRun:
    """
    Executes end-to-end data acquisition:
    Extract -> Validate -> Normalize -> Match -> Load -> Alert Generation
    Tracks run status and metrics in collection_runs.
    """
    if source_id is None:
        source = db.execute(select(DataSource).where(DataSource.name == connector.name)).scalar_one_or_none()
        if source:
            source_id = source.id

    run = CollectionRun(
        source_id=source_id,
        started_at=datetime.now(UTC),
        status="running",
        records_extracted=0,
        records_loaded=0,
        error_count=0,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        raw_items = list(connector.extract())
        run.records_extracted = len(raw_items)

        normalized = [normalize_record(item) for item in raw_items]
        loaded_count = load_validated_records(db, normalized, collection_run_id=run.id)

        # Trigger alert engine
        generate_alerts(db)

        run.records_loaded = loaded_count
        run.status = "completed"
        run.finished_at = datetime.now(UTC)
        db.commit()
        logger.info("Pipeline run #%d completed successfully. Loaded %d records.", run.id, loaded_count)

    except Exception as exc:
        logger.exception("Pipeline run #%d failed: %s", run.id, exc)
        run.status = "failed"
        run.error_count = 1
        run.error_message = str(exc)
        run.finished_at = datetime.now(UTC)
        db.commit()

    return run
