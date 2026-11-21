from __future__ import annotations

import httpx

from app.connectors.base import BaseConnector, ExtractedRecord


class MockAPIConnector(BaseConnector):
    name = "mock_api"

    def __init__(self, base_url: str = "http://localhost:8001/api/products"):
        self.base_url = base_url

    def extract(self):
        payload = {"products": []}
        response = httpx.get(self.base_url, timeout=10)
        response.raise_for_status()
        payload = response.json()
        records = []
        for item in payload.get("products", []):
            records.append(ExtractedRecord(
                title=item.get("title", "Unknown product"),
                brand=item.get("brand", "Unknown"),
                model_number=item.get("model_number"),
                sku=item.get("sku"),
                gtin=item.get("gtin"),
                category=item.get("category", "General"),
                current_price=item.get("current_price", 0),
                original_price=item.get("original_price"),
                currency=item.get("currency", "USD"),
                availability=item.get("availability", "in_stock"),
                retailer=item.get("retailer", "Mock Retailer"),
                product_url=item.get("product_url"),
                extracted_at=item.get("extracted_at"),
                source=self.name,
                metadata={"api": self.base_url},
            ))
        return records
