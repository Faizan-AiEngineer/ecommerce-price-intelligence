from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any


@dataclass
class ExtractedRecord:
    title: str
    brand: str
    model_number: str | None
    sku: str | None
    gtin: str | None
    category: str
    current_price: Decimal
    original_price: Decimal | None
    currency: str
    availability: str
    retailer: str
    product_url: str | None
    extracted_at: datetime
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseConnector:
    name: str = "base"

    def extract(self) -> Iterable[ExtractedRecord]:
        raise NotImplementedError

    def validate_record(self, record: ExtractedRecord) -> bool:
        return bool(record.title and record.current_price >= Decimal(0))
