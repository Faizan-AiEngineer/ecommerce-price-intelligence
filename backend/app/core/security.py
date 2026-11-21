from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app.core.config import get_settings

settings = get_settings()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(api_key: str | None = Depends(api_key_header)) -> str:
    if not settings.auth_required:
        return "local-dev"
    if api_key == settings.api_key:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="API key required. For local development, pass X-API-Key: dev-local-key or set AUTH_REQUIRED=false.",
    )
