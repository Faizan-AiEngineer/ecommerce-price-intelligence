from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.init_db import initialize_database
from app.db.session import engine
from app.models.models import Product, Retailer
from app.services.demo_seed import seed_demo_database


def bootstrap_demo_database() -> None:
    initialize_database()
    # Keep the entire seed in one transaction even though the seeder commits in stages.
    with engine.begin() as connection, Session(bind=connection, join_transaction_mode="rollback_only") as db:
        if db.scalar(select(Product.id).limit(1)) is None and db.scalar(select(Retailer.id).limit(1)) is None:
            seed_demo_database(db)


if __name__ == "__main__":
    bootstrap_demo_database()
