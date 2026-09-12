"""Analytics and progress endpoints."""

from app.services.analytics_service import analytics_service
from fastapi import APIRouter

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("")
def get_analytics():
    """Retrieve progress metrics, exercise distribution, and historical score trends."""
    return analytics_service.get_progress_overview()
