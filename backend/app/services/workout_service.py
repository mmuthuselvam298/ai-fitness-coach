"""Workout session management, processing lifecycle, and persistence orchestration."""

import time
import uuid
from datetime import datetime, timezone
from typing import Any

import numpy as np
from app.core.logging import logger
from app.exercises.base import ExerciseAnalyzer
from app.exercises.registry import ExerciseRegistry
from app.models.database import db
from app.services.feedback_service import FeedbackService
from app.vision.pose_detector import PoseDetector


class ActiveSession:
    def __init__(
        self,
        session_id: str,
        exercise: str,
        target_reps: int,
        detector: PoseDetector | None = None,
    ):
        self.session_id = session_id
        self.exercise = exercise
        self.target_reps = target_reps
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.start_perf_time = time.time()
        self.analyzer: ExerciseAnalyzer = ExerciseRegistry.create_analyzer(exercise)
        self.detector: PoseDetector | None = detector
        self.feedback_service = FeedbackService()
        self.total_frames_processed = 0
        self.is_finished = False


class WorkoutService:
    def __init__(self):
        self.active_sessions: dict[str, ActiveSession] = {}
        # Shared detector for reuse to avoid recreating models
        self.shared_detector = PoseDetector()

    def start_session(self, exercise: str, target_reps: int = 10) -> dict[str, Any]:
        session_id = str(uuid.uuid4())
        session = ActiveSession(
            session_id=session_id,
            exercise=exercise,
            target_reps=target_reps,
            detector=self.shared_detector,
        )
        self.active_sessions[session_id] = session

        # Save initial session in DB
        db.save_session(
            {
                "id": session_id,
                "exercise": exercise,
                "started_at": session.started_at,
                "target_reps": target_reps,
                "status": "in_progress",
            }
        )
        logger.info(f"Started workout session {session_id} for {exercise}")
        return {
            "session_id": session_id,
            "exercise": exercise,
            "target_reps": target_reps,
            "started_at": session.started_at,
        }

    def process_frame(
        self,
        session_id: str,
        frame_bgr: np.ndarray,
        timestamp: float | None = None,
    ) -> dict[str, Any]:
        """Process image frame through detection and exercise state machine."""
        session = self.active_sessions.get(session_id)
        if not session or session.is_finished:
            return {"error": "Invalid or expired session"}

        session.total_frames_processed += 1
        now = timestamp if timestamp is not None else time.time()

        # 1. Pose Detection
        det_result = session.detector.detect(frame_bgr, timestamp=now)

        if not det_result["detected"]:
            return {
                "detected": False,
                "error": det_result.get("error", "No person detected"),
                "rep_count": session.analyzer.rep_count,
                "phase": session.analyzer.current_phase,
                "confidence": 0.0,
                "inference_ms": det_result["inference_ms"],
                "form_score": session.analyzer.get_average_form_score(),
                "feedback": [
                    {
                        "type": "presence",
                        "severity": "warning",
                        "message": det_result.get("error", "Stand in full view of the camera"),
                    }
                ],
            }

        # 2. Exercise State Machine
        landmarks = det_result["landmarks"]
        analysis = session.analyzer.process_frame(landmarks, timestamp=now)

        # 3. Filter feedback prompts
        filtered_fb = session.feedback_service.filter_feedback(analysis.feedback)

        # 4. If a rep completed, persist immediately to database
        if analysis.rep_completed and analysis.completed_rep_details:
            rep_data = analysis.completed_rep_details
            db.save_rep_result(
                {
                    "session_id": session_id,
                    "rep_number": rep_data.rep_number,
                    "duration_seconds": rep_data.duration_seconds,
                    "form_score": rep_data.form_score,
                    "depth_score": rep_data.depth_score,
                    "alignment_score": rep_data.alignment_score,
                    "consistency_score": rep_data.consistency_score,
                    "primary_feedback": rep_data.primary_feedback,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                }
            )

        # 5. Persist notable feedback events
        for fb in filtered_fb:
            if fb.severity.value in ["warning", "error", "good"]:
                db.save_feedback_event(
                    {
                        "session_id": session_id,
                        "rep_number": session.analyzer.rep_count,
                        "type": fb.type,
                        "severity": fb.severity.value,
                        "message": fb.message,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

        # Format landmarks for JSON response
        lms_json = {
            int(k): {"x": round(p.x, 4), "y": round(p.y, 4), "visibility": round(p.visibility, 3)}
            for k, p in landmarks.items()
        }

        return {
            "detected": True,
            "multiple_people": det_result.get("multiple_people", False),
            "rep_count": analysis.rep_count,
            "phase": analysis.phase,
            "primary_angle": analysis.primary_angle,
            "angles": analysis.angles,
            "form_score": analysis.form_score,
            "confidence": det_result["confidence"],
            "inference_ms": det_result["inference_ms"],
            "feedback": [f.to_dict() for f in filtered_fb],
            "rep_completed": analysis.rep_completed,
            "is_calibrated": analysis.is_calibrated,
            "calibration_message": analysis.calibration_message,
            "landmarks": lms_json,
        }

    def process_landmarks(
        self,
        session_id: str,
        landmarks: dict[int, Any],
        timestamp: float | None = None,
    ) -> dict[str, Any]:
        """Process pre-extracted landmarks (e.g. from synthetic generator or client-side MediaPipe)."""
        session = self.active_sessions.get(session_id)
        if not session or session.is_finished:
            return {"error": "Invalid or expired session"}

        from app.vision.geometry import Point3D
        pt_landmarks: dict[int, Point3D] = {}
        for k, v in landmarks.items():
            pt_landmarks[int(k)] = Point3D(
                x=float(v.get("x", 0)),
                y=float(v.get("y", 0)),
                z=float(v.get("z", 0)),
                visibility=float(v.get("visibility", 1.0)),
                presence=float(v.get("presence", 1.0)),
            )

        now = timestamp if timestamp is not None else time.time()
        analysis = session.analyzer.process_frame(pt_landmarks, timestamp=now)
        filtered_fb = session.feedback_service.filter_feedback(analysis.feedback)

        if analysis.rep_completed and analysis.completed_rep_details:
            rep_data = analysis.completed_rep_details
            db.save_rep_result(
                {
                    "session_id": session_id,
                    "rep_number": rep_data.rep_number,
                    "duration_seconds": rep_data.duration_seconds,
                    "form_score": rep_data.form_score,
                    "depth_score": rep_data.depth_score,
                    "alignment_score": rep_data.alignment_score,
                    "consistency_score": rep_data.consistency_score,
                    "primary_feedback": rep_data.primary_feedback,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                }
            )

        return {
            "detected": True,
            "rep_count": analysis.rep_count,
            "phase": analysis.phase,
            "primary_angle": analysis.primary_angle,
            "angles": analysis.angles,
            "form_score": analysis.form_score,
            "feedback": [f.to_dict() for f in filtered_fb],
            "rep_completed": analysis.rep_completed,
            "is_calibrated": analysis.is_calibrated,
        }

    def finish_session(self, session_id: str) -> dict[str, Any]:
        session = self.active_sessions.get(session_id)
        if not session:
            # Check if exists in DB
            db_session = db.get_session(session_id)
            if db_session:
                return db_session
            raise ValueError(f"Session not found: {session_id}")

        session.is_finished = True
        duration = round(time.time() - session.start_perf_time, 1)
        avg_score = session.analyzer.get_average_form_score()
        breakdown = session.analyzer.get_score_breakdown()
        completed_reps = session.analyzer.rep_count

        # Produce actionable summary insights
        what_went_well = []
        focus_next_time = []

        if breakdown["depth"] >= 85:
            what_went_well.append("Consistent exercise depth across reps")
        else:
            focus_next_time.append("Focus on reaching full range of motion at bottom")

        if breakdown["alignment"] >= 80:
            what_went_well.append("Maintained stable posture and alignment")
        else:
            focus_next_time.append("Keep posture upright and avoid excessive leaning or sagging")

        if breakdown["consistency"] >= 85:
            what_went_well.append("Smooth and controlled movement cadence")
        else:
            focus_next_time.append("Control the descent tempo - avoid rushing or bouncing")

        if not what_went_well:
            what_went_well.append("Completed workout session with tracked movement")
        if not focus_next_time:
            focus_next_time.append("Maintain this excellent biomechanical form in your next set")

        session_record = {
            "id": session_id,
            "exercise": session.exercise,
            "started_at": session.started_at,
            "ended_at": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": duration,
            "target_reps": session.target_reps,
            "completed_reps": completed_reps,
            "average_form_score": avg_score,
            "depth_score": breakdown["depth"],
            "alignment_score": breakdown["alignment"],
            "consistency_score": breakdown["consistency"],
            "status": "completed",
            "notes": f"Completed {completed_reps}/{session.target_reps} reps",
        }
        db.save_session(session_record)

        summary = {
            **session_record,
            "reps_detail": [r.to_dict() for r in session.analyzer.completed_reps],
            "what_went_well": what_went_well,
            "focus_next_time": focus_next_time,
        }

        # Cleanup memory
        del self.active_sessions[session_id]
        return summary


workout_service = WorkoutService()
