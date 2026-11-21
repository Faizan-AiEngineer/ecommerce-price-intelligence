from __future__ import annotations

import logging
import signal
import sys
import time

from app.connectors.demo_catalog import DemoCatalogConnector
from app.core.config import get_settings
from app.db.init_db import initialize_database
from app.db.session import SessionLocal
from app.scheduler.scheduler import PriceMonitoringScheduler
from app.services.etl import run_collection_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("priceintel.scheduler")
settings = get_settings()


def execute_scheduled_pipeline() -> None:
    logger.info("Executing scheduled competitor price collection...")
    db = SessionLocal()
    try:
        connector = DemoCatalogConnector(seed=int(time.time()), item_count=50)
        run = run_collection_pipeline(db, connector)
        logger.info(
            "Scheduled collection completed: run #%d status=%s extracted=%d loaded=%d",
            run.id,
            run.status,
            run.records_extracted,
            run.records_loaded,
        )
    except Exception as exc:
        logger.exception("Error executing scheduled collection: %s", exc)
    finally:
        db.close()


def main() -> None:
    logger.info("Starting Price Intelligence Scheduler Worker...")
    initialize_database()

    scheduler = PriceMonitoringScheduler(
        interval_minutes=settings.collection_interval_minutes,
        timezone=settings.scheduler_timezone,
    )
    scheduler.add_recurring_collection_job(execute_scheduled_pipeline)
    scheduler.start()

    def handle_exit(signum, frame):
        logger.info("Termination signal received. Shutting down scheduler...")
        scheduler.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    # Execute once on startup to ensure freshness
    try:
        execute_scheduled_pipeline()
    except Exception as err:
        logger.error("Initial startup collection encountered error: %s", err)

    logger.info("Scheduler worker is active and awaiting next interval.")
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    main()
