from __future__ import annotations

from sqlalchemy import create_engine

from app.core.config import get_settings
from app.db.session import Base
from app.models.models import Product  # noqa: F401


def initialize_database() -> None:
    settings = get_settings()
    engine = create_engine(settings.database_url, future=True)
    Base.metadata.create_all(bind=engine)
