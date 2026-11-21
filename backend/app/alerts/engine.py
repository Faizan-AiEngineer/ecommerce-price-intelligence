from __future__ import annotations

import logging
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.models import PriceAlert, PriceHistory, Retailer, RetailerProduct

logger = logging.getLogger(__name__)


def generate_alerts(
    db: Session,
    price_change_threshold_pct: Decimal = Decimal("5.0"),
    reference_retailer_name: str | None = None,
) -> int:
    """
    Scans recent pricing and stock changes to generate actionable alerts:
    - price_drop: price decreased by >= threshold %
    - price_increase: price increased by >= threshold %
    - competitor_undercut: competitor price dropped below reference retailer price
    - out_of_stock: item transitioned to out_of_stock
    - back_in_stock: item returned to stock
    Deduplicates against existing active alerts.
    """
    alerts_created = 0

    # 1. Fetch active alerts index to prevent duplicate alerts
    existing_active = db.execute(
        select(PriceAlert.product_id, PriceAlert.retailer_product_id, PriceAlert.alert_type)
        .where(PriceAlert.status == "active")
    ).all()
    active_keys: set[tuple[int, int | None, str]] = {
        (row[0], row[1], row[2]) for row in existing_active
    }

    # 2. Check each RetailerProduct for price and stock transitions
    retailer_products = db.execute(select(RetailerProduct)).scalars().all()
    for rp in retailer_products:
        # Fetch last 2 observations for this offer
        recent_obs = db.execute(
            select(PriceHistory)
            .where(PriceHistory.retailer_product_id == rp.id)
            .order_by(desc(PriceHistory.observed_at))
            .limit(2)
        ).scalars().all()

        if len(recent_obs) >= 2:
            latest = recent_obs[0]
            prev = recent_obs[1]

            # Price Change checks
            if prev.observed_price > Decimal(0):
                diff = latest.observed_price - prev.observed_price
                pct_change = (diff / prev.observed_price) * Decimal(100)

                # Price Drop
                if pct_change <= -price_change_threshold_pct:
                    alert_key = (rp.product_id, rp.id, "price_drop")
                    if alert_key not in active_keys:
                        db.add(PriceAlert(
                            product_id=rp.product_id,
                            retailer_product_id=rp.id,
                            alert_type="price_drop",
                            previous_value=prev.observed_price,
                            current_value=latest.observed_price,
                            threshold=price_change_threshold_pct,
                            status="active",
                            created_at=datetime.now(UTC),
                        ))
                        active_keys.add(alert_key)
                        alerts_created += 1

                # Price Increase
                elif pct_change >= price_change_threshold_pct:
                    alert_key = (rp.product_id, rp.id, "price_increase")
                    if alert_key not in active_keys:
                        db.add(PriceAlert(
                            product_id=rp.product_id,
                            retailer_product_id=rp.id,
                            alert_type="price_increase",
                            previous_value=prev.observed_price,
                            current_value=latest.observed_price,
                            threshold=price_change_threshold_pct,
                            status="active",
                            created_at=datetime.now(UTC),
                        ))
                        active_keys.add(alert_key)
                        alerts_created += 1

            # Stock Transition checks
            prev_in_stock = prev.stock_status in ("in_stock", "limited")
            curr_in_stock = latest.stock_status in ("in_stock", "limited")

            if prev_in_stock and not curr_in_stock:
                alert_key = (rp.product_id, rp.id, "out_of_stock")
                if alert_key not in active_keys:
                    db.add(PriceAlert(
                        product_id=rp.product_id,
                        retailer_product_id=rp.id,
                        alert_type="out_of_stock",
                        previous_value=None,
                        current_value=None,
                        threshold=None,
                        status="active",
                        created_at=datetime.now(UTC),
                    ))
                    active_keys.add(alert_key)
                    alerts_created += 1
            elif not prev_in_stock and curr_in_stock:
                alert_key = (rp.product_id, rp.id, "back_in_stock")
                if alert_key not in active_keys:
                    db.add(PriceAlert(
                        product_id=rp.product_id,
                        retailer_product_id=rp.id,
                        alert_type="back_in_stock",
                        previous_value=None,
                        current_value=latest.observed_price,
                        threshold=None,
                        status="active",
                        created_at=datetime.now(UTC),
                    ))
                    active_keys.add(alert_key)
                    alerts_created += 1

    # 3. Competitor Undercutting checks
    # Find reference retailer
    ref_retailer = None
    if reference_retailer_name:
        ref_retailer = db.execute(
            select(Retailer).where(Retailer.name == reference_retailer_name)
        ).scalar_one_or_none()
    if not ref_retailer:
        # Default to first active retailer
        ref_retailer = db.execute(
            select(Retailer).where(Retailer.active.is_(True)).order_by(Retailer.id)
        ).scalars().first()

    if ref_retailer:
        ref_offers = db.execute(
            select(RetailerProduct).where(RetailerProduct.retailer_id == ref_retailer.id)
        ).scalars().all()
        ref_map = {ro.product_id: ro for ro in ref_offers}

        for comp_rp in retailer_products:
            if comp_rp.retailer_id == ref_retailer.id:
                continue
            ref_rp = ref_map.get(comp_rp.product_id)
            if ref_rp and comp_rp.current_price < ref_rp.current_price:
                alert_key = (comp_rp.product_id, comp_rp.id, "competitor_undercut")
                if alert_key not in active_keys:
                    db.add(PriceAlert(
                        product_id=comp_rp.product_id,
                        retailer_product_id=comp_rp.id,
                        alert_type="competitor_undercut",
                        previous_value=ref_rp.current_price,
                        current_value=comp_rp.current_price,
                        threshold=ref_rp.current_price - comp_rp.current_price,
                        status="active",
                        created_at=datetime.now(UTC),
                    ))
                    active_keys.add(alert_key)
                    alerts_created += 1

    db.commit()
    logger.info("Generated %d new alerts.", alerts_created)
    return alerts_created
