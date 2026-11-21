from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.connectors.demo_catalog import DemoCatalogConnector
from app.core.security import require_api_key
from app.db.session import SessionLocal
from app.models.models import CollectionRun, DataSource
from app.services.etl import run_collection_pipeline

router = APIRouter(prefix="/jobs", tags=["jobs"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/sources")
async def list_sources(db: Session = Depends(get_db)):
    sources = db.execute(select(DataSource).order_by(DataSource.id)).scalars().all()
    return {
        "items": [
            {
                "id": s.id,
                "name": s.name,
                "source_type": s.source_type,
                "configuration": s.configuration,
                "enabled": s.enabled,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in sources
        ]
    }


@router.get("")
async def list_jobs(db: Session = Depends(get_db), _: str = Depends(require_api_key)):
    runs = (
        db.execute(
            select(CollectionRun, DataSource.name.label("source_name"))
            .join(DataSource, DataSource.id == CollectionRun.source_id, isouter=True)
            .order_by(desc(CollectionRun.started_at))
            .limit(50)
        )
        .all()
    )

    items = []
    for run, src_name in runs:
        duration_sec = None
        if run.finished_at and run.started_at:
            duration_sec = round((run.finished_at - run.started_at).total_seconds(), 2)

        items.append({
            "id": run.id,
            "source_id": run.source_id,
            "source_name": src_name or "Demo Catalog",
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "finished_at": run.finished_at.isoformat() if run.finished_at else None,
            "duration_seconds": duration_sec,
            "status": run.status,
            "records_extracted": run.records_extracted,
            "records_loaded": run.records_loaded,
            "error_count": run.error_count,
            "error_message": run.error_message,
        })

    return {"items": items}


@router.post("/trigger")
@router.post("/{job_id}/run")
async def run_job(job_id: int = 1, db: Session = Depends(get_db), _: str = Depends(require_api_key)):
    # Trigger a demo extraction collection pipeline run
    connector = DemoCatalogConnector(seed=42, item_count=50)
    run = run_collection_pipeline(db, connector)

    return {
        "id": run.id,
        "source_name": connector.name,
        "status": run.status,
        "records_extracted": run.records_extracted,
        "records_loaded": run.records_loaded,
        "error_message": run.error_message,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "finished_at": run.finished_at.isoformat() if run.finished_at else None,
    }
