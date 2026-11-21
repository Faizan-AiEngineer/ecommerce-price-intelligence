from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.config import get_settings

router = APIRouter(prefix="/settings", tags=["settings"])

settings = get_settings()

# In-memory runtime configuration store (defaults initialized from environment)
runtime_config = {
    "app_name": settings.app_name,
    "app_env": settings.app_env,
    "base_currency": settings.base_currency,
    "collection_interval_minutes": settings.collection_interval_minutes,
    "scheduler_timezone": settings.scheduler_timezone,
    "alert_price_drop_threshold_pct": 5.0,
    "alert_price_increase_threshold_pct": 5.0,
    "reference_retailer": "MarketHub",
    "auth_required": settings.auth_required,
}


class SettingsUpdate(BaseModel):
    base_currency: str = Field(default="USD")
    collection_interval_minutes: int = Field(default=60, ge=5, le=1440)
    scheduler_timezone: str = Field(default="UTC")
    alert_price_drop_threshold_pct: float = Field(default=5.0, ge=0.5, le=90.0)
    alert_price_increase_threshold_pct: float = Field(default=5.0, ge=0.5, le=90.0)
    reference_retailer: str = Field(default="MarketHub")


@router.get("")
async def get_app_settings():
    return runtime_config


@router.put("")
async def update_app_settings(payload: SettingsUpdate):
    runtime_config.update(payload.model_dump())
    return {
        "status": "success",
        "message": "Settings updated successfully",
        "settings": runtime_config,
    }
