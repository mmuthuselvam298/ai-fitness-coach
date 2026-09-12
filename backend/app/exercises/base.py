"""Base exercise analyzer architecture, schemas, and state machine contracts."""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.vision.geometry import Point3D


class FeedbackSeverity(str, Enum):
    INFO = "info"
    GOOD = "good"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class FeedbackEvent:
    type: str
    severity: FeedbackSeverity
    message: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "severity": self.severity.value,
            "message": self.message,
            "timestamp": round(self.timestamp, 2),
        }


@dataclass
class RepResult:
    rep_number: int
    duration_seconds: float
    form_score: float
    depth_score: float
    alignment_score: float
    consistency_score: float
    primary_feedback: str
    completed_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rep_number": self.rep_number,
            "duration_seconds": round(self.duration_seconds, 2),
            "form_score": round(self.form_score, 1),
            "depth_score": round(self.depth_score, 1),
            "alignment_score": round(self.alignment_score, 1),
            "consistency_score": round(self.consistency_score, 1),
            "primary_feedback": self.primary_feedback,
            "completed_at": round(self.completed_at, 2),
        }


@dataclass
class AnalysisFrame:
    exercise: str
    rep_count: int
    phase: str
    primary_angle: float
    angles: dict[str, float]
    form_score: float
    feedback: list[FeedbackEvent]
    is_calibrated: bool
    calibration_message: str | None
    rep_completed: bool = False
    completed_rep_details: RepResult | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "exercise": self.exercise,
            "rep_count": self.rep_count,
            "phase": self.phase,
            "primary_angle": round(self.primary_angle, 1),
            "angles": {k: round(v, 1) for k, v in self.angles.items()},
            "form_score": round(self.form_score, 1),
            "feedback": [fb.to_dict() for fb in self.feedback],
            "is_calibrated": self.is_calibrated,
            "calibration_message": self.calibration_message,
            "rep_completed": self.rep_completed,
            "completed_rep_details": (
                self.completed_rep_details.to_dict() if self.completed_rep_details else None
            ),
        }


class ExerciseAnalyzer(ABC):
    """Abstract base class for biomechanical exercise analyzers."""

    def __init__(self, exercise_name: str):
        self.exercise_name = exercise_name
        self.rep_count: int = 0
        self.current_phase: str = "READY"
        self.rep_start_time: float | None = None
        self.completed_reps: list[RepResult] = []
        self.active_feedback: list[FeedbackEvent] = []
        self.current_rep_feedback: list[FeedbackEvent] = []

    @abstractmethod
    def get_required_landmarks(self) -> list[int]:
        """List of landmark indices required for robust analysis."""

    @abstractmethod
    def process_frame(
        self,
        landmarks: dict[int, Point3D],
        timestamp: float | None = None,
    ) -> AnalysisFrame:
        """Process extracted landmarks for one frame and return analysis."""

    @abstractmethod
    def reset(self):
        """Reset state machine and counters."""
        self.rep_count = 0
        self.current_phase = "READY"
        self.rep_start_time = None
        self.completed_reps.clear()
        self.active_feedback.clear()
        self.current_rep_feedback.clear()

    def get_average_form_score(self) -> float:
        if not self.completed_reps:
            return 85.0  # Default initial baseline
        scores = [r.form_score for r in self.completed_reps]
        return round(float(sum(scores) / len(scores)), 1)

    def get_score_breakdown(self) -> dict[str, float]:
        if not self.completed_reps:
            return {"depth": 85.0, "alignment": 85.0, "consistency": 85.0}
        d = sum(r.depth_score for r in self.completed_reps) / len(self.completed_reps)
        a = sum(r.alignment_score for r in self.completed_reps) / len(self.completed_reps)
        c = sum(r.consistency_score for r in self.completed_reps) / len(self.completed_reps)
        return {
            "depth": round(d, 1),
            "alignment": round(a, 1),
            "consistency": round(c, 1),
        }
