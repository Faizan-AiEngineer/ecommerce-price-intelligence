# API Documentation: E-commerce Competitor Price Intelligence

All API endpoints are prefixed with `/api/v1`. OpenAPI documentation and interactive Swagger UI are available at `/docs`.

## 1. System Health
### `GET /api/v1/health`
Checks API server availability.
- **Response**: `200 OK`
```json
{
  "status": "ok",
  "service": "price-intelligence-api"
}
```

---

## 2. Dashboard Analytics
### `GET /api/v1/dashboard/summary`
Returns high-level business KPIs, category breakdowns, retailer coverage, and 30-day market price trend aggregations.
- **Response**: `200 OK`
```json
{
  "monitored_products": 500,
  "active_retailers": 3,
  "active_offers": 1500,
  "average_product_price": 342.14,
  "recent_price_drops": 24,
  "out_of_stock_products": 12,
  "active_alerts": 38,
  "last_successful_collection": "2026-11-13T12:00:00Z",
  "price_trends": [
    {"date": "2026-11-01", "avg_price": 338.50, "min_price": 45.00, "max_price": 890.00}
  ],
  "category_distribution": [
    {"category": "Laptops", "product_count": 84, "avg_price": 450.20}
  ],
  "retailer_summary": [
    {"retailer": "MarketHub", "offer_count": 500, "avg_price": 339.80}
  ]
}
```

---

## 3. Product Catalog
### `GET /api/v1/products`
Lists canonical products with pagination, search, and stock filters.
- **Query Parameters**:
  - `q`: Search keyword (name, brand, model)
  - `category`: Category name filter
  - `stock`: `in_stock` or `out_of_stock`
  - `limit`: Default 25 (max 200)
  - `offset`: Pagination offset

### `GET /api/v1/products/{id}`
Returns product details and all retailer offers.

### `GET /api/v1/products/{id}/price-history`
Returns chronological price snapshots by retailer for interactive charts.

---

## 4. Competitor Benchmarking
### `GET /api/v1/competitors/comparison`
Computes head-to-head pricing disparity between a reference store and competitors.
- **Query Parameters**:
  - `reference_retailer`: Retailer ID (required)
  - `category`: Optional category filter
  - `limit`: Page limit
  - `offset`: Page offset

---

## 5. Alerts & Notifications
### `GET /api/v1/alerts`
Lists system alerts filtered by status or trigger type (`price_drop`, `competitor_undercut`, `out_of_stock`).

### `PATCH /api/v1/alerts/{id}`
Updates alert status (`acknowledged`, `resolved`).
```json
{
  "status": "acknowledged"
}
```

---

## 6. Jobs & Automation
### `GET /api/v1/jobs`
Lists collection run audit history.

### `POST /api/v1/jobs/trigger`
Triggers an immediate collection run.

---

## 7. Reports & Data Export
### `GET /api/v1/reports/export?file_format=csv`
Streams CSV formatted report.
### `GET /api/v1/reports/export?file_format=xlsx`
Streams Microsoft Excel formatted workbook.
