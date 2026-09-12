"""Frame and video analysis endpoints."""

import base64
import os
import shutil
import tempfile
import time

import cv2
import numpy as np
from app.core.logging import logger
from app.exercises.registry import ExerciseRegistry
from app.vision.pose_detector import PoseDetector
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

router = APIRouter(prefix="/analyze", tags=["Analysis"])

# Shared detector
pose_detector = PoseDetector()


class FrameAnalysisRequest(BaseModel):
    exercise: str
    image_base64: str
    timestamp: float | None = None


@router.post("/frame")
def analyze_single_frame(req: FrameAnalysisRequest):
    """Analyze a single base64 encoded frame."""
    try:
        analyzer = ExerciseRegistry.create_analyzer(req.exercise)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        # Decode base64
        header_split = req.image_base64.split(",")
        encoded = header_split[1] if len(header_split) > 1 else header_split[0]
        img_bytes = base64.b64decode(encoded)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        frame_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame_bgr is None:
            raise ValueError("Failed to decode image data")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image decoding failed: {e!s}")

    det = pose_detector.detect(frame_bgr, timestamp=req.timestamp)
    if not det["detected"]:
        return {
            "detected": False,
            "error": det.get("error", "No person detected"),
            "confidence": 0.0,
            "inference_ms": det["inference_ms"],
        }

    analysis = analyzer.process_frame(det["landmarks"], timestamp=req.timestamp)

    return {
        "detected": True,
        "multiple_people": det.get("multiple_people", False),
        "exercise": req.exercise,
        "rep_count": analysis.rep_count,
        "phase": analysis.phase,
        "primary_angle": analysis.primary_angle,
        "angles": analysis.angles,
        "form_score": analysis.form_score,
        "confidence": det["confidence"],
        "inference_ms": det["inference_ms"],
        "feedback": [f.to_dict() for f in analysis.feedback],
        "is_calibrated": analysis.is_calibrated,
        "calibration_message": analysis.calibration_message,
    }


@router.post("/video")
async def analyze_uploaded_video(
    file: UploadFile = File(...),
    exercise: str = Form("squat"),
    frame_skip: int = Form(2),
):
    """Process an uploaded workout video file and return full session metrics.

    Privacy: Video file is stored temporarily and automatically destroyed after processing.
    """
    try:
        analyzer = ExerciseRegistry.create_analyzer(exercise)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Save to secure temporary directory
    temp_dir = tempfile.mkdtemp(prefix="formfit_video_")
    temp_file_path = os.path.join(temp_dir, file.filename or "upload.mp4")

    try:
        with open(temp_file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        cap = cv2.VideoCapture(temp_file_path)
        if not cap.isOpened():
            raise HTTPException(status_code=400, detail="Unable to read video file format")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        frame_idx = 0
        processed_frames = 0
        start_time = time.perf_counter()
        detector = PoseDetector()

        timeline = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % frame_skip == 0:
                ts = frame_idx / fps
                det = detector.detect(frame, timestamp=ts)
                if det["detected"]:
                    analysis = analyzer.process_frame(det["landmarks"], timestamp=ts)
                    timeline.append(
                        {
                            "time_seconds": round(ts, 2),
                            "phase": analysis.phase,
                            "angle": round(analysis.primary_angle, 1),
                            "reps": analysis.rep_count,
                            "feedback": [fb.message for fb in analysis.feedback],
                        }
                    )
                processed_frames += 1

            frame_idx += 1

        cap.release()
        total_time = time.perf_counter() - start_time

        avg_fps = round(processed_frames / total_time, 1) if total_time > 0 else 0
        avg_score = analyzer.get_average_form_score()
        breakdown = analyzer.get_score_breakdown()

        return {
            "exercise": exercise,
            "total_video_frames": total_frames,
            "processed_frames": processed_frames,
            "processing_time_seconds": round(total_time, 2),
            "effective_fps": avg_fps,
            "completed_reps": analyzer.rep_count,
            "average_form_score": avg_score,
            "score_breakdown": breakdown,
            "reps_detail": [r.to_dict() for r in analyzer.completed_reps],
            "timeline": timeline[::3],  # downsample timeline for payload efficiency
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process video: {e!s}")
    finally:
        # Privacy guarantee: Always delete uploaded media files immediately
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass
