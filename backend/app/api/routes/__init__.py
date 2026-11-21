from app.api.routes.alerts import router as alerts_router
from app.api.routes.competitors import router as competitors_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.health import router as health_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.products import router as products_router
from app.api.routes.reports import router as reports_router
from app.api.routes.retailers import router as retailers_router

__all__ = [
    "alerts_router",
    "competitors_router",
    "dashboard_router",
    "health_router",
    "jobs_router",
    "products_router",
    "reports_router",
    "retailers_router",
]
