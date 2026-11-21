from __future__ import annotations

import logging
from datetime import UTC, datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


class PriceMonitoringScheduler:
    def __init__(self, interval_minutes: int = 60, timezone: str = "UTC") -> None:
        self.interval_minutes = interval_minutes
        self.timezone = timezone
        self.scheduler = BackgroundScheduler(timezone=timezone)
        self._last_run_time: datetime | None = None

    def add_recurring_collection_job(self, task_func, job_id: str = "recurring_price_collection"):
        """
        Adds interval job with max_instances=1 to strictly prevent overlapping executions.
        coalesce=True ensures missed executions roll into one single run after restart/lag.
        """
        job = self.scheduler.add_job(
            func=task_func,
            trigger=IntervalTrigger(minutes=self.interval_minutes, timezone=self.timezone),
            id=job_id,
            name="Competitor Price Collection Pipeline",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=300,
        )
        logger.info("Configured recurring collection job '%s' every %d minutes.", job_id, self.interval_minutes)
        return job

    def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Price monitoring scheduler started.")

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Price monitoring scheduler stopped.")

    def mark_run(self) -> None:
        self._last_run_time = datetime.now(UTC)

    def last_run(self) -> datetime | None:
        return self._last_run_time
