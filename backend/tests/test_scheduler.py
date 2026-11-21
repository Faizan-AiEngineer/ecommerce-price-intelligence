from __future__ import annotations

from app.scheduler.scheduler import PriceMonitoringScheduler


def test_scheduler_initialization_and_overlap_prevention() -> None:
    scheduler = PriceMonitoringScheduler(interval_minutes=30)
    assert scheduler.interval_minutes == 30
    assert scheduler.last_run() is None

    # Verify job configuration
    def dummy_task():
        pass

    job = scheduler.add_recurring_collection_job(dummy_task, job_id="test_job")
    assert job.id == "test_job"
    assert job.max_instances == 1  # Strictly prevents overlapping executions

    # Mark run and check timestamp
    scheduler.mark_run()
    assert scheduler.last_run() is not None
