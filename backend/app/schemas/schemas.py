from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class RetailerBase(BaseModel):
    name: str
    website: str
    currency: str = "USD"
    country: str = "US"
    active: bool = True


class RetailerCreate(RetailerBase):
    pass


class RetailerOut(RetailerBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductBase(BaseModel):
    canonical_name: str
    brand: str = ""
    category: str = ""
    model_number: str | None = None
    gtin: str | None = None
    description: str | None = None


class ProductCreate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RetailerProductOut(BaseModel):
    id: int
    retailer_id: int
    product_id: int
    retailer_sku: str | None
    product_url: str | None
    retailer_product_name: str
    current_price: Decimal
    currency: str
    stock_status: str
    last_checked_at: datetime
    retailer_name: str | None = None
    product_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PriceHistoryOut(BaseModel):
    id: int
    retailer_product_id: int
    observed_price: Decimal
    original_price: Decimal | None
    currency: str
    stock_status: str
    observed_at: datetime
    collection_run_id: int | None

    model_config = ConfigDict(from_attributes=True)


class DashboardSummary(BaseModel):
    monitored_products: int
    active_retailers: int
    active_offers: int
    average_product_price: Decimal
    recent_price_drops: int
    out_of_stock_products: int
    active_alerts: int
    last_successful_collection: datetime | None


class CompetitorComparison(BaseModel):
    reference_retailer: str
    retailer: str
    product_name: str
    current_price: Decimal
    competitor_price: Decimal
    absolute_difference: Decimal
    percentage_difference: Decimal
    cheaper_competitor: bool


class AlertOut(BaseModel):
    id: int
    product_id: int
    retailer_product_id: int | None
    alert_type: str
    previous_value: Decimal | None
    current_value: Decimal | None
    threshold: Decimal | None
    created_at: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)


class AlertUpdate(BaseModel):
    status: Literal["active", "acknowledged", "resolved"] = "acknowledged"


class JobStatusOut(BaseModel):
    id: int
    source_id: int | None
    started_at: datetime
    finished_at: datetime | None
    status: str
    records_extracted: int
    records_loaded: int
    error_count: int
    error_message: str | None

    model_config = ConfigDict(from_attributes=True)


class DataSourceOut(BaseModel):
    id: int
    name: str
    source_type: str
    configuration: dict[str, Any] | None
    enabled: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExportRequest(BaseModel):
    format: Literal["csv", "xlsx"] = Field(default="csv")
