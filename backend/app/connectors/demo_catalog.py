from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.analytics.pricing import normalize_currency, normalize_price
from app.connectors.base import BaseConnector, ExtractedRecord


class DemoCatalogConnector(BaseConnector):
    name = "demo_catalog"

    def __init__(self, seed: int = 42, item_count: int = 500):
        self.seed = seed
        self.item_count = item_count

    def extract(self):
        rng = random.Random(self.seed)
        categories = ["Laptops", "Smartphones", "Audio", "Wearables", "Home Office", "Accessories"]
        brands = ["Apex", "NorthPeak", "NovaCore", "Helio", "Summit", "Orbitel"]
        retailers = ["MarketHub", "ValueCart", "PrimeSelect"]
        records = []
        for idx in range(self.item_count):
            category = categories[idx % len(categories)]
            brand = brands[idx % len(brands)]
            model = f"{brand}-{category[:3].upper()}-{idx + 1:04d}"
            title = f"{brand} {category.removesuffix('s')} {model}"
            price = Decimal(str(round(49 + (idx * 1.7 % 899), 2)))
            original = price * Decimal("1.12")
            retailer = retailers[idx % len(retailers)]
            availability = "in_stock" if idx % 5 else "limited"
            record = ExtractedRecord(
                title=title,
                brand=brand,
                model_number=model,
                sku=f"SKU-{idx + 1:06d}",
                gtin=f"978{idx + 1:012d}",
                category=category,
                current_price=normalize_price(price),
                original_price=normalize_price(original),
                currency=normalize_currency("USD"),
                availability=availability,
                retailer=retailer,
                product_url=f"https://example.com/products/{idx + 1}",
                extracted_at=datetime.now(UTC) - timedelta(days=rng.randint(0, 12)),
                source=self.name,
                metadata={"seed": self.seed, "index": idx},
            )
            records.append(record)
        return records
