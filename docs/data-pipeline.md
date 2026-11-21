# Data Pipeline & ETL Architecture

## 1. Pipeline Stages

The ingestion lifecycle executes deterministically across 5 core stages:

```
[Extract] --> [Validate & Normalize] --> [Product Match] --> [Idempotent Load] --> [Alert Evaluation]
```

### Stage 1: Extraction
Connectors implement `BaseConnector.extract()` returning standardized `ExtractedRecord` objects containing raw metadata, pricing, source URL, and timestamp.

### Stage 2: Validation & Normalization
- Strip non-numeric currency symbols (`$`, `€`, `£`, commas).
- Convert prices to `Decimal(precision=12, scale=2)`. Reject negative prices.
- Map currency variants (`usd`, `$`) to standard ISO 4217 (`USD`).
- Normalize availability strings (`In Stock`, `limited`) to standardized snake_case status.

### Stage 3: Product Matching
Resolves seller records against canonical catalog items:
1. **GTIN Match**: Exact match on 13/14-digit Global Trade Item Number.
2. **Brand & Model Match**: Exact match on manufacturer brand name and alphanumeric model number.
3. **Canonical Title Match**: Fallback match on cleaned product name.

### Stage 4: Idempotent Load
- Upserts canonical `Product` records.
- Upserts `RetailerProduct` offer records with updated `current_price` and `last_checked_at`.
- Inserts time-series `PriceHistory` snapshot, enforcing unique constraints on `(retailer_product_id, observed_at, observed_price)`.

### Stage 5: Alert Generation
The alert engine examines price deltas and competitor undercutting to record actionable alerts in `price_alerts`.
Redundant alerts for identical conditions are deduplicated.
