# Portfolio Case Study: E-commerce Competitor Price Intelligence

## 1. Executive Summary
Designed and built a full-stack competitor price intelligence demo. The system ingests and reconciles product offerings across multiple digital storefronts, detects dynamic pricing strategies, and surfaces competitor undercutting after collection.

---

## 2. Architectural Decisions & Trade-Offs

### 2.1 Deterministic Product Matching vs. Fuzzy Matching
- **Decision**: Implemented strict hierarchical matching prioritizing exact GTIN/EAN, then Brand + Model Number, followed by a canonical-name match.
- **Rationale**: In e-commerce price monitoring, false-positive matches (comparing a 512GB laptop to a 256GB model) invalidate competitor undercutting alerts and compromise pricing decisions. High precision was prioritized over aggressive merge recall.

### 2.2 Financial Calculations with Python `Decimal`
- **Decision**: Enforced PostgreSQL `NUMERIC(12, 2)` and used Python `Decimal` for price normalization and comparisons.
- **Rationale**: Binary floating-point representation (`float`) introduces precision artifacts (e.g., `0.1 + 0.2 = 0.30000000000000004`), which lead to incorrect percentage difference calculations and duplicate alert triggers.

### 2.3 Idempotent Pipeline Design
- **Decision**: Enforced compound uniqueness on `(retailer_product_id, observed_at, observed_price)` alongside upsert logic on `RetailerProduct`.
- **Rationale**: Distributed crawlers and scheduled retries frequently re-read identical page states. Without idempotency, duplicate history points distort moving-average price calculations and create artificial volatility.

### 2.4 Decoupled Scheduler Architecture
- **Decision**: Implemented the recurring background scheduler as an isolated daemon service configured with `max_instances=1` and `coalesce=True`.
- **Rationale**: Avoids running duplicated timers across multi-worker ASGI web servers (e.g. Uvicorn with multiple workers), with overlap prevention for the recurring job within each scheduler instance.

---

## 3. Measurable Deliverables

- **Synthetic Demo Data**: 500 canonical products, 3 distinct retail storefronts, 1,500 active offers, and 135,000 historical price snapshots across a 90-day window.
- **Automated Test Coverage**: 17 unit and integration tests across ETL normalization, pricing mathematics, database constraints, alert engine logic, and REST endpoints.
- **Frontend Capabilities**: 7 responsive dashboard views built with React 18, TypeScript, Recharts, and Tailwind CSS.
- **Data Export**: Streaming CSV and Excel export for business intelligence integration.
