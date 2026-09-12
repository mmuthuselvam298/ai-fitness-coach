"""Workout sessions management endpoints."""

import base64
from typing import Any

import cv2
import numpy as np
from app.models.database import db
from app.services.workout_service import workout_service
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/workouts", tags=["Workouts"])


class StartWorkoutRequest(BaseModel):
    exercise: str
    target_reps: int = Field(default=12, ge=1, le=100)


class SessionFrameRequest(BaseModel):
    image_base64: str
    timestamp: float | None = None


class SessionLandmarksRequest(BaseModel):
    landmarks: dict[str, Any]
    timestamp: float | None = None


@router.post("/start")
def start_workout(req: StartWorkoutRequest):
    """Initializes a new workout session."""
    try:
        return workout_service.start_session(
            exercise=req.exercise, target_reps=req.target_reps
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/frame")
def submit_frame(session_id: str, req: SessionFrameRequest):
    """Submit an active video frame to an in-progress session."""
    try:
        header_split = req.image_base64.split(",")
        encoded = header_split[1] if len(header_split) > 1 else header_split[0]
        img_bytes = base64.b64decode(encoded)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame_bgr is None:
            raise ValueError("Invalid image")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image decoding failed: {e}")

    result = workout_service.process_frame(
        session_id=session_id, frame_bgr=frame_bgr, timestamp=req.timestamp
    )
    if "error" in result and result["error"] == "Invalid or expired session":
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/{session_id}/landmarks")
def submit_landmarks(session_id: str, req: SessionLandmarksRequest):
    """Submit pre-extracted landmarks to the session."""
    result = workout_service.process_landmarks(
        session_id=session_id, landmarks=req.landmarks, timestamp=req.timestamp
    )
    if "error" in result and result["error"] == "Invalid or expired session":
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/{session_id}/finish")
def finish_workout(session_id: str):
    """Finalize workout session and compute summary metrics."""
    try:
        return workout_service.finish_session(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("")
def list_workouts(
    limit: int = Query(default=20, ge=1, le=100),
    exercise: str | None = None,
):
    """Retrieve history of completed workout sessions."""
    return db.get_sessions(limit=limit, exercise=exercise)


@router.get("/{session_id}")
def get_workout(session_id: str):
    """Retrieve detailed session report including reps and feedback events."""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
