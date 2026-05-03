from __future__ import annotations

from fastapi import APIRouter

from app.config import load_settings
from app.services.health import check_backend_health


router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def get_health() -> dict[str, object]:
    settings = load_settings()
    return check_backend_health(settings).as_dict()

