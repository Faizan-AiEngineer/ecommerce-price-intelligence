from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Retailer(Base):
    __tablename__ = "retailers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    website: Mapped[str] = mapped_column(String(255), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    country: Mapped[str] = mapped_column(String(80), default="US")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    retailer_products: Mapped[list[RetailerProduct]] = relationship(back_populates="retailer")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    canonical_name: Mapped[str] = mapped_column(String(250), nullable=False)
    brand: Mapped[str] = mapped_column(String(120), default="")
    category: Mapped[str] = mapped_column(String(100), default="")
    model_number: Mapped[str | None] = mapped_column(String(120), nullable=True)
    gtin: Mapped[str | None] = mapped_column(String(30), nullable=True, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    retailer_products: Mapped[list[RetailerProduct]] = relationship(back_populates="product")
    price_alerts: Mapped[list[PriceAlert]] = relationship(back_populates="product")


class RetailerProduct(Base):
    __tablename__ = "retailer_products"
    __table_args__ = (UniqueConstraint("retailer_id", "product_id", name="uq_retailer_product"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    retailer_id: Mapped[int] = mapped_column(ForeignKey("retailers.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    retailer_sku: Mapped[str | None] = mapped_column(String(80), nullable=True)
    product_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    retailer_product_name: Mapped[str] = mapped_column(String(250), default="")
    current_price: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    stock_status: Mapped[str] = mapped_column(String(30), default="in_stock")
    last_checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    retailer: Mapped[Retailer] = relationship(back_populates="retailer_products")
    product: Mapped[Product] = relationship(back_populates="retailer_products")
    price_history: Mapped[list[PriceHistory]] = relationship(back_populates="retailer_product")
    price_alerts: Mapped[list[PriceAlert]] = relationship(back_populates="retailer_product")


class PriceHistory(Base):
    __tablename__ = "price_history"
    __table_args__ = (UniqueConstraint("retailer_product_id", "observed_at", "observed_price", name="uq_price_history_observation"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    retailer_product_id: Mapped[int] = mapped_column(ForeignKey("retailer_products.id"), nullable=False)
    observed_price: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), nullable=False)
    original_price: Mapped[Decimal | None] = mapped_column(Numeric(precision=12, scale=2), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    stock_status: Mapped[str] = mapped_column(String(30), default="in_stock")
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    collection_run_id: Mapped[int | None] = mapped_column(ForeignKey("collection_runs.id"), nullable=True)

    retailer_product: Mapped[RetailerProduct] = relationship(back_populates="price_history")


class CollectionRun(Base):
    __tablename__ = "collection_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("data_sources.id"), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="queued")
    records_extracted: Mapped[int] = mapped_column(default=0)
    records_loaded: Mapped[int] = mapped_column(default=0)
    error_count: Mapped[int] = mapped_column(default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)


class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    retailer_product_id: Mapped[int | None] = mapped_column(ForeignKey("retailer_products.id"), nullable=True)
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    previous_value: Mapped[Decimal | None] = mapped_column(Numeric(precision=12, scale=2), nullable=True)
    current_value: Mapped[Decimal | None] = mapped_column(Numeric(precision=12, scale=2), nullable=True)
    threshold: Mapped[Decimal | None] = mapped_column(Numeric(precision=12, scale=2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str] = mapped_column(String(30), default="active")

    product: Mapped[Product] = relationship(back_populates="price_alerts")
    retailer_product: Mapped[RetailerProduct | None] = relationship(back_populates="price_alerts")


class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(80), nullable=False)
    configuration: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


__all__ = [
    "CollectionRun",
    "DataSource",
    "PriceAlert",
    "PriceHistory",
    "Product",
    "Retailer",
    "RetailerProduct",
]
