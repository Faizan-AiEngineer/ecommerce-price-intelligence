from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Add backend directory to sys.path so app packages are resolvable
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.db.init_db import initialize_database
from app.db.session import SessionLocal
from app.models.models import (
    CollectionRun,
    DataSource,
    PriceAlert,
    PriceHistory,
    Product,
    Retailer,
    RetailerProduct,
)
from app.services.demo_seed import seed_demo_database

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed_demo")


def run_seed(reset: bool = True, product_count: int = 500, history_days: int = 90) -> None:
    logger.info("Initializing database schema...")
    initialize_database()

    db = SessionLocal()
    try:
        if reset:
            logger.info("Resetting existing demo records...")
            db.query(PriceAlert).delete()
            db.query(PriceHistory).delete()
            db.query(RetailerProduct).delete()
            db.query(CollectionRun).delete()
            db.query(DataSource).delete()
            db.query(Product).delete()
            db.query(Retailer).delete()
            db.commit()

        logger.info(
            "Seeding demo data (products=%d, history_days=%d)...",
            product_count,
            history_days,
        )
        stats = seed_demo_database(db, product_count=product_count, history_days=history_days)
        logger.info("Seed successful! Summary: %s", stats)
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed E-commerce Price Intelligence demo data.")
    parser.add_argument("--no-reset", action="store_true", help="Do not wipe existing records before seeding")
    parser.add_argument("--products", type=int, default=500, help="Number of canonical products to generate (default: 500)")
    parser.add_argument("--days", type=int, default=90, help="Days of price history to generate (default: 90)")

    args = parser.parse_args()
    run_seed(reset=not args.no_reset, product_count=args.products, history_days=args.days)
