from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from decimal import Decimal

from playwright.async_api import async_playwright

from app.connectors.base import BaseConnector, ExtractedRecord


class PlaywrightStorefrontConnector(BaseConnector):
    name = "playwright_storefront"

    def __init__(self, base_url: str = "http://localhost:3000", headless: bool = True):
        self.base_url = base_url
        self.headless = headless

    async def _extract_async(self):
        async with async_playwright() as browser_manager:
            browser = await browser_manager.chromium.launch(headless=self.headless)
            page = await browser.new_page()
            await page.goto(self.base_url, timeout=25000)
            cards = await page.locator("[data-testid='product-card']").all()
            records = []
            for card in cards:
                title = await card.locator("[data-testid='product-title']").inner_text()
                price_text = await card.locator("[data-testid='product-price']").inner_text()
                records.append(ExtractedRecord(
                    title=title,
                    brand="Demo Brand",
                    model_number=None,
                    sku=None,
                    gtin=None,
                    category="Demo",
                    current_price=Decimal(str(price_text.replace("$", "").replace(",", ""))),
                    original_price=None,
                    currency="USD",
                    availability="in_stock",
                    retailer="Local Demo Store",
                    product_url=self.base_url,
                    extracted_at=datetime.now(UTC),
                    source=self.name,
                    metadata={"selector": "product-card"},
                ))
            await browser.close()
            return records

    def extract(self):
        return asyncio.run(self._extract_async())
