"""Application configuration using Pydantic Settings."""

import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "FormFit AI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ]

    # Database
    DATABASE_PATH: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data",
        "formfit.db",
    )

    # MediaPipe Pose Estimation
    POSE_MODEL_COMPLEXITY: int = 1
    MIN_DETECTION_CONFIDENCE: float = 0.5
    MIN_TRACKING_CONFIDENCE: float = 0.5
    MIN_LANDMARK_VISIBILITY: float = 0.60

    # Smoothing Configuration
    SMOOTHING_ENABLED: bool = True
    SMOOTHING_METHOD: str = "ema"  # "ema" or "one_euro"
    SMOOTHING_ALPHA: float = 0.65
    ONE_EURO_MIN_CUTOFF: float = 1.0
    ONE_EURO_BETA: float = 0.007

    # File uploads & limits
    MAX_UPLOAD_SIZE_MB: int = 50

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
