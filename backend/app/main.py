"""FastAPI application main entrypoint."""

import os

from app.api import (
    routes_analysis,
    routes_analytics,
    routes_demo,
    routes_exercises,
    routes_health,
    routes_workouts,
    ws_workout,
)
from app.core.config import settings
from app.models.database import init_db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Initialize SQLite database
init_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Biomechanical real-time pose estimation, repetition counter, and form analysis engine.",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers with /api prefix
api_prefix = "/api"
app.include_router(routes_health.router, prefix=api_prefix)
app.include_router(routes_exercises.router, prefix=api_prefix)
app.include_router(routes_analysis.router, prefix=api_prefix)
app.include_router(routes_workouts.router, prefix=api_prefix)
app.include_router(routes_analytics.router, prefix=api_prefix)
app.include_router(routes_demo.router, prefix=api_prefix)
app.include_router(ws_workout.router, prefix=api_prefix)

# Serve demo video files if available
demo_media_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "demo"
)
if os.path.exists(demo_media_dir):
    app.mount("/static/demo", StaticFiles(directory=demo_media_dir), name="demo_static")


@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs",
        "supported_exercises": ["squat", "pushup", "bicep_curl"],
        "message": "FormFit AI Computer Vision Engine is running.",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
    )
