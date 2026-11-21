from __future__ import annotations

from contextlib import asynccontextmanager, suppress
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.routes import (
    alerts,
    competitors,
    dashboard,
    health,
    jobs,
    products,
    reports,
    retailers,
)
from app.api.routes import (
    settings as app_settings_route,
)
from app.core.config import get_settings
from app.db.init_db import initialize_database

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema on startup
    with suppress(Exception):
        initialize_database()
    yield


app = FastAPI(
    title="E-commerce Competitor Price Intelligence System",
    description="Centralized platform to monitor competitor product prices, availability, discounts, and historical trends across multiple retailers.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.api_v1_prefix)
app.include_router(dashboard.router, prefix=settings.api_v1_prefix)
app.include_router(products.router, prefix=settings.api_v1_prefix)
app.include_router(retailers.router, prefix=settings.api_v1_prefix)
app.include_router(competitors.router, prefix=settings.api_v1_prefix)
app.include_router(alerts.router, prefix=settings.api_v1_prefix)
app.include_router(jobs.router, prefix=settings.api_v1_prefix)
app.include_router(reports.router, prefix=settings.api_v1_prefix)
app.include_router(app_settings_route.router, prefix=settings.api_v1_prefix)


STATIC_DIR = Path(__file__).resolve().parent / "static"


@app.get("/")
def root():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "system": "E-commerce Competitor Price Intelligence System",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs",
    }
