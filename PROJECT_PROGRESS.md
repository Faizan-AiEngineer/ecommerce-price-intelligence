# Project Progress Checklist: E-commerce Competitor Price Intelligence System

## Phase 1: Architecture and Setup
- [x] Inspect the development environment and confirm local tool availability.
- [x] Establish monorepo structure: backend, frontend, data, scripts, docs, and deployment workflows.
- [x] Create system architecture documentation and data flow diagrams.
- [x] Configure backend package, database models, and settings management.
- [x] Configure Docker Compose for PostgreSQL, FastAPI, React, and Scheduler.

## Phase 2: Database and Demo Data
- [x] Implement SQLAlchemy 2.x ORM models for retailers, products, offers, history, runs, alerts, and sources.
- [x] Create Alembic migration baseline (`001_initial_schema.py`).
- [x] Build deterministic synthetic catalog generator (500 products, 3 retailers, 90-day history).
- [x] Implement reproducible CLI seed script (`scripts/seed_demo.py`).
- [x] Verify database relationships, compound indexes, and unique constraints.

## Phase 3: Data Collection
- [x] Implement modular `BaseConnector` interface with metadata and validation.
- [x] Implement `DemoCatalogConnector` for deterministic extraction.
- [x] Implement `MockAPIConnector` for REST API data harvesting.
- [x] Implement `PlaywrightStorefrontConnector` for browser-based sample storefront extraction.
- [x] Add extraction logging, error handling, and request timeouts.

## Phase 4: ETL Pipeline and Matching
- [x] Implement data normalization (currencies, ISO standards, Decimal monetary values).
- [x] Implement deduplication engine and invalid record filtering.
- [x] Implement deterministic product matching (GTIN -> Brand/Model -> Canonical Name).
- [x] Implement idempotent database loading preventing duplicate observations.
- [x] Track collection runs and batch metrics in `collection_runs`.

## Phase 5: Analytics and API
- [x] Implement pricing metrics and daily price statistics over the preceding 30 days.
- [x] Implement competitor comparison engine (absolute & percentage differences, undercut detection).
- [x] Implement automated alert engine (price drop, increase, competitor undercut, stock transitions).
- [x] Expose REST endpoints with FastAPI (Swagger docs at `/docs`).
- [x] Implement analytical data exports (streaming CSV and Excel `.xlsx`).

## Phase 6: Frontend Dashboard
- [x] Scaffold modern React 18 + TypeScript + Vite + Tailwind CSS application.
- [x] Implement Page 1: Overview Dashboard with KPI cards, Recharts Area/Bar charts, and live activity feed.
- [x] Implement Page 2: Product Explorer with search, category/stock filtering, and pagination.
- [x] Implement Page 3: Product Detail with matched offers table and multi-retailer historical price chart.
- [x] Implement Page 4: Competitor Comparison with head-to-head metrics and undercutting badges.
- [x] Implement Page 5: Alerts Feed with trigger details and acknowledge action.
- [x] Implement Page 6: Collection Jobs Monitor with run status, duration, and manual trigger button.
- [x] Implement Page 7: Settings & Analytics Export hub.

## Phase 7: Scheduling and Automation
- [x] Implement APScheduler background engine with configurable intervals.
- [x] Implement strict overlap prevention (`max_instances=1`) and coalesce handling.
- [x] Create standalone daemon scheduler worker (`python -m app.scheduler.worker`).
- [x] Add manual on-demand pipeline trigger endpoint (`POST /api/v1/jobs/trigger`).

## Phase 8: Testing and Deployment
- [x] Implement automated test suite covering all core modules (17 tests).
- [x] Validate price normalization, deduplication, and percentage difference logic.
- [x] Validate ETL pipeline idempotency and database constraints.
- [x] Validate alert engine threshold evaluation and deduplication.
- [x] Configure multi-stage Docker build for frontend (Nginx) and backend (Python 3.13).
- [x] Configure GitHub Actions CI workflow for backend and frontend quality checks.

## Phase 9: Documentation and Portfolio Delivery
- [x] Comprehensive GitHub README with architecture diagrams and instructions.
- [x] Detailed portfolio case study explaining engineering challenges and design choices.
- [x] Complete API guide, database schema documentation, and deployment instructions.
