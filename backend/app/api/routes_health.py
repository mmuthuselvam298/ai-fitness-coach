"""Health check endpoint and system telemetry."""

import os

from app.core.config import settings
from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
def get_health():
    """Returns system status, active configuration, and model status."""
    model_exists = os.path.exists(
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "models",
            "weights",
            "pose_landmarker_lite.task",
        )
    )

    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "vision_engine": {
            "model": "MediaPipe PoseLandmarker Tasks API",
            "model_ready": model_exists,
            "smoothing_enabled": settings.SMOOTHING_ENABLED,
            "smoothing_method": settings.SMOOTHING_METHOD,
            "min_visibility": settings.MIN_LANDMARK_VISIBILITY,
        },
    }
