"""MediaPipe Pose Landmarker detector and skeleton overlay renderer."""

import os
import time
from typing import Any

import cv2
import mediapipe as mp
import numpy as np
from app.core.config import settings
from app.core.logging import logger
from app.vision.geometry import Point3D, PoseLandmark
from app.vision.smoothing import LandmarkSmoother

# MediaPipe Tasks API
BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


# Standard pose skeleton connections for visualization
POSE_CONNECTIONS = [
    (PoseLandmark.LEFT_SHOULDER, PoseLandmark.RIGHT_SHOULDER),
    (PoseLandmark.LEFT_SHOULDER, PoseLandmark.LEFT_ELBOW),
    (PoseLandmark.LEFT_ELBOW, PoseLandmark.LEFT_WRIST),
    (PoseLandmark.RIGHT_SHOULDER, PoseLandmark.RIGHT_ELBOW),
    (PoseLandmark.RIGHT_ELBOW, PoseLandmark.RIGHT_WRIST),
    (PoseLandmark.LEFT_SHOULDER, PoseLandmark.LEFT_HIP),
    (PoseLandmark.RIGHT_SHOULDER, PoseLandmark.RIGHT_HIP),
    (PoseLandmark.LEFT_HIP, PoseLandmark.RIGHT_HIP),
    (PoseLandmark.LEFT_HIP, PoseLandmark.LEFT_KNEE),
    (PoseLandmark.LEFT_KNEE, PoseLandmark.LEFT_ANKLE),
    (PoseLandmark.RIGHT_HIP, PoseLandmark.RIGHT_KNEE),
    (PoseLandmark.RIGHT_KNEE, PoseLandmark.RIGHT_ANKLE),
]


class PoseDetector:
    """Wrapper around MediaPipe PoseLandmarker Tasks API with smoothing and multi-person handling."""

    def __init__(
        self,
        model_path: str | None = None,
        min_detection_confidence: float = settings.MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence: float = settings.MIN_TRACKING_CONFIDENCE,
        enable_smoothing: bool = settings.SMOOTHING_ENABLED,
    ):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        default_model = os.path.join(base_dir, "models", "weights", "pose_landmarker_lite.task")
        self.model_path = model_path or default_model

        if not os.path.exists(self.model_path):
            logger.warning(f"Model file not found at {self.model_path}, downloading...")
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            import urllib.request
            url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task"
            urllib.request.urlretrieve(url, self.model_path)
            logger.info("Model download complete.")

        options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=self.model_path),
            running_mode=VisionRunningMode.IMAGE,
            min_pose_detection_confidence=min_detection_confidence,
            min_pose_presence_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            num_poses=2,  # Detect up to 2 to identify multi-person edge case
        )
        self.detector = PoseLandmarker.create_from_options(options)

        self.smoother = (
            LandmarkSmoother(
                method=settings.SMOOTHING_METHOD,
                alpha=settings.SMOOTHING_ALPHA,
                one_euro_min_cutoff=settings.ONE_EURO_MIN_CUTOFF,
                one_euro_beta=settings.ONE_EURO_BETA,
            )
            if enable_smoothing
            else None
        )

    def detect(
        self, frame_bgr: np.ndarray, timestamp: float | None = None
    ) -> dict[str, Any]:
        """Detect pose in a BGR frame (OpenCV format).

        Returns:
            Dict with:
            - 'detected': bool
            - 'multiple_people': bool
            - 'landmarks': Dict[int, Point3D] (index -> Point3D)
            - 'confidence': float (0.0 to 1.0)
            - 'inference_ms': float
            - 'error': Optional[str]
        """
        start_t = time.perf_counter()

        if frame_bgr is None or frame_bgr.size == 0:
            return {
                "detected": False,
                "multiple_people": False,
                "landmarks": {},
                "confidence": 0.0,
                "inference_ms": 0.0,
                "error": "Empty or invalid frame",
            }

        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Run inference
        result = self.detector.detect(mp_image)
        inference_ms = (time.perf_counter() - start_t) * 1000.0

        if not result.pose_landmarks or len(result.pose_landmarks) == 0:
            return {
                "detected": False,
                "multiple_people": False,
                "landmarks": {},
                "confidence": 0.0,
                "inference_ms": round(inference_ms, 2),
                "error": "No person detected in frame",
            }

        multiple_people = len(result.pose_landmarks) > 1

        # Select the most prominent person (index 0 has highest detection score)
        raw_landmarks = result.pose_landmarks[0]
        extracted: dict[int, Point3D] = {}
        confidences: list[float] = []

        for idx, lm in enumerate(raw_landmarks):
            vis = float(getattr(lm, "visibility", 1.0) or 1.0)
            presence = float(getattr(lm, "presence", 1.0) or 1.0)
            confidences.append(vis)
            extracted[idx] = Point3D(
                x=float(lm.x),
                y=float(lm.y),
                z=float(lm.z) if hasattr(lm, "z") else 0.0,
                visibility=vis,
                presence=presence,
            )

        # Apply temporal smoothing if enabled
        if self.smoother is not None:
            processed_landmarks = self.smoother.smooth(extracted, timestamp)
        else:
            processed_landmarks = extracted

        avg_confidence = float(np.mean(confidences)) if confidences else 0.0

        return {
            "detected": True,
            "multiple_people": multiple_people,
            "landmarks": processed_landmarks,
            "confidence": round(avg_confidence, 3),
            "inference_ms": round(inference_ms, 2),
            "error": "Please ensure only one person is in the frame" if multiple_people else None,
        }

    def reset_smoothing(self):
        if self.smoother is not None:
            self.smoother.reset()

    def close(self):
        try:
            self.detector.close()
        except Exception:
            pass


def draw_pose_overlay(
    frame_bgr: np.ndarray,
    landmarks: dict[int, Point3D],
    primary_angle: float | None = None,
    feedback_text: str | None = None,
    rep_count: int | None = None,
    phase: str | None = None,
) -> np.ndarray:
    """Renders a clean, aesthetic pose skeleton and telemetry overlay onto an image frame."""
    canvas = frame_bgr.copy()
    h, w = canvas.shape[:2]

    # Draw skeleton connections
    for start_idx, end_idx in POSE_CONNECTIONS:
        pt1 = landmarks.get(int(start_idx))
        pt2 = landmarks.get(int(end_idx))
        if pt1 and pt2 and pt1.visibility >= 0.5 and pt2.visibility >= 0.5:
            x1, y1 = int(pt1.x * w), int(pt1.y * h)
            x2, y2 = int(pt2.x * w), int(pt2.y * h)
            # Fresh green line: BGR (129, 185, 16)
            cv2.line(canvas, (x1, y1), (x2, y2), (16, 185, 129), 3, cv2.LINE_AA)

    # Draw key landmarks
    for idx, pt in landmarks.items():
        if pt.visibility >= 0.5:
            cx, cy = int(pt.x * w), int(pt.y * h)
            # Outer ring
            cv2.circle(canvas, (cx, cy), 6, (255, 255, 255), -1, cv2.LINE_AA)
            # Inner circle (charcoal / green)
            cv2.circle(canvas, (cx, cy), 4, (16, 185, 129), -1, cv2.LINE_AA)

    # Minimal athletic HUD box in upper left
    hud_bg = canvas.copy()
    cv2.rectangle(hud_bg, (15, 15), (280, 115), (28, 30, 33), -1)
    cv2.addWeighted(hud_bg, 0.7, canvas, 0.3, 0, canvas)

    # Telemetry text
    if rep_count is not None:
        cv2.putText(
            canvas,
            f"REPS: {rep_count}",
            (30, 50),
            cv2.FONT_HERSHEY_DUPLEX,
            1.0,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
    if phase:
        cv2.putText(
            canvas,
            f"Phase: {phase.upper()}",
            (30, 78),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (16, 185, 129),
            1,
            cv2.LINE_AA,
        )
    if primary_angle is not None:
        cv2.putText(
            canvas,
            f"Angle: {int(primary_angle)} deg",
            (30, 102),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (200, 200, 200),
            1,
            cv2.LINE_AA,
        )

    # Feedback prompt banner at bottom
    if feedback_text:
        fb_bg = canvas.copy()
        cv2.rectangle(fb_bg, (20, h - 60), (w - 20, h - 15), (28, 30, 33), -1)
        cv2.addWeighted(fb_bg, 0.8, canvas, 0.2, 0, canvas)
        cv2.putText(
            canvas,
            feedback_text,
            (35, h - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

    return canvas
