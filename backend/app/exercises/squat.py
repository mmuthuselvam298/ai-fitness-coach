"""Squat exercise biomechanical analyzer and state machine."""

import time

from app.exercises.base import (
    AnalysisFrame,
    ExerciseAnalyzer,
    FeedbackEvent,
    FeedbackSeverity,
    RepResult,
)
from app.vision.geometry import (
    Point3D,
    PoseLandmark,
    are_landmarks_visible,
    calculate_angle,
    calculate_vertical_angle,
)


class SquatAnalyzer(ExerciseAnalyzer):
    """Biomechanical analyzer for squats.

    Tracks knee flexion, hip hinge, and torso vertical alignment.
    State Machine:
        READY -> DESCENDING -> BOTTOM -> ASCENDING -> COMPLETED -> READY
    """

    # Knee angle thresholds
    STANDING_KNEE_ANGLE = 160.0  # Above this is upright standing
    DESCENDING_TRIGGER = 150.0  # Started moving down
    PARALLEL_DEPTH_TARGET = 95.0  # Thigh parallel to floor
    SHALLOW_THRESHOLD = 110.0   # Cutoff for counting a rep
    ASCENDING_TRIGGER = 115.0   # Moving back up

    def __init__(self):
        super().__init__(exercise_name="squat")
        self.min_knee_angle_in_rep = 180.0
        self.max_torso_angle_in_rep = 0.0
        self.preferred_side = "right"

    def get_required_landmarks(self) -> list[int]:
        # Either left or right leg + hip + shoulder must be visible
        return [
            PoseLandmark.LEFT_HIP,
            PoseLandmark.LEFT_KNEE,
            PoseLandmark.LEFT_ANKLE,
            PoseLandmark.RIGHT_HIP,
            PoseLandmark.RIGHT_KNEE,
            PoseLandmark.RIGHT_ANKLE,
        ]

    def _determine_active_side(self, landmarks: dict[int, Point3D]) -> str:
        """Picks left or right side based on higher average landmark visibility."""
        left_lms = [
            landmarks.get(PoseLandmark.LEFT_HIP),
            landmarks.get(PoseLandmark.LEFT_KNEE),
            landmarks.get(PoseLandmark.LEFT_ANKLE),
            landmarks.get(PoseLandmark.LEFT_SHOULDER),
        ]
        right_lms = [
            landmarks.get(PoseLandmark.RIGHT_HIP),
            landmarks.get(PoseLandmark.RIGHT_KNEE),
            landmarks.get(PoseLandmark.RIGHT_ANKLE),
            landmarks.get(PoseLandmark.RIGHT_SHOULDER),
        ]

        left_vis = (
            sum(p.visibility for p in left_lms if p is not None) / 4.0
            if all(p is not None for p in left_lms)
            else 0.0
        )
        right_vis = (
            sum(p.visibility for p in right_lms if p is not None) / 4.0
            if all(p is not None for p in right_lms)
            else 0.0
        )

        return "left" if left_vis > right_vis else "right"

    def process_frame(
        self,
        landmarks: dict[int, Point3D],
        timestamp: float | None = None,
    ) -> AnalysisFrame:
        now = timestamp if timestamp is not None else time.time()
        self.active_feedback = []

        # 1. Calibration / Visibility verification
        side = self._determine_active_side(landmarks)
        self.preferred_side = side

        if side == "left":
            shld_idx = PoseLandmark.LEFT_SHOULDER
            hip_idx = PoseLandmark.LEFT_HIP
            knee_idx = PoseLandmark.LEFT_KNEE
            ankl_idx = PoseLandmark.LEFT_ANKLE
        else:
            shld_idx = PoseLandmark.RIGHT_SHOULDER
            hip_idx = PoseLandmark.RIGHT_HIP
            knee_idx = PoseLandmark.RIGHT_KNEE
            ankl_idx = PoseLandmark.RIGHT_ANKLE

        req_indices = [shld_idx, hip_idx, knee_idx, ankl_idx]
        visible, missing = are_landmarks_visible(landmarks, req_indices, min_visibility=0.55)

        if not visible:
            calib_msg = "Ensure full body is visible in camera view"
            return AnalysisFrame(
                exercise=self.exercise_name,
                rep_count=self.rep_count,
                phase=self.current_phase,
                primary_angle=180.0,
                angles={},
                form_score=self.get_average_form_score(),
                feedback=[FeedbackEvent("calibration", FeedbackSeverity.WARNING, calib_msg)],
                is_calibrated=False,
                calibration_message=calib_msg,
            )

        shoulder = landmarks[shld_idx]
        hip = landmarks[hip_idx]
        knee = landmarks[knee_idx]
        ankle = landmarks[ankl_idx]

        # 2. Joint Angles
        knee_angle = calculate_angle(hip, knee, ankle)
        hip_angle = calculate_angle(shoulder, hip, knee)
        torso_angle = calculate_vertical_angle(shoulder, hip)

        rep_completed = False
        completed_rep: RepResult | None = None

        # 3. State Machine Transitions
        if self.current_phase == "READY":
            self.min_knee_angle_in_rep = 180.0
            self.max_torso_angle_in_rep = 0.0

            if knee_angle <= self.DESCENDING_TRIGGER:
                self.current_phase = "DESCENDING"
                self.rep_start_time = now
                self.min_knee_angle_in_rep = knee_angle
                self.max_torso_angle_in_rep = torso_angle

        elif self.current_phase == "DESCENDING":
            self.min_knee_angle_in_rep = min(self.min_knee_angle_in_rep, knee_angle)
            self.max_torso_angle_in_rep = max(self.max_torso_angle_in_rep, torso_angle)

            # Check if reached bottom inflection (depth reached or starting to reverse)
            if knee_angle <= self.PARALLEL_DEPTH_TARGET:
                self.current_phase = "BOTTOM"
                self.active_feedback.append(
                    FeedbackEvent("depth", FeedbackSeverity.GOOD, "Good squat depth!")
                )
            elif knee_angle > self.min_knee_angle_in_rep + 8.0:
                # Started ascending prematurely before hitting optimal target
                if self.min_knee_angle_in_rep <= self.SHALLOW_THRESHOLD:
                    self.current_phase = "ASCENDING"
                else:
                    # Incomplete attempt / jitter, reset to READY
                    self.current_phase = "READY"
                    self.active_feedback.append(
                        FeedbackEvent("depth", FeedbackSeverity.WARNING, "Squat deeper - hips below knees")
                    )

        elif self.current_phase == "BOTTOM":
            self.min_knee_angle_in_rep = min(self.min_knee_angle_in_rep, knee_angle)
            self.max_torso_angle_in_rep = max(self.max_torso_angle_in_rep, torso_angle)

            # If knee angle begins expanding upward
            if knee_angle > self.min_knee_angle_in_rep + 5.0:
                self.current_phase = "ASCENDING"

        elif self.current_phase == "ASCENDING":
            self.max_torso_angle_in_rep = max(self.max_torso_angle_in_rep, torso_angle)

            # Check if returned upright
            if knee_angle >= self.STANDING_KNEE_ANGLE:
                self.current_phase = "COMPLETED"
                self.rep_count += 1
                rep_completed = True

                # Compute Rep Score & Metrics
                duration = max(now - (self.rep_start_time or now), 0.5)

                # Depth Score (40%)
                if self.min_knee_angle_in_rep <= 90.0:
                    depth_score = 100.0
                    primary_msg = "Great depth"
                elif self.min_knee_angle_in_rep <= 100.0:
                    depth_score = 88.0
                    primary_msg = "Good parallel squat"
                elif self.min_knee_angle_in_rep <= 110.0:
                    depth_score = 65.0
                    primary_msg = "Slightly shallow"
                else:
                    depth_score = 45.0
                    primary_msg = "Lower hips further"

                # Alignment Score (35%): Torso uprightness
                if self.max_torso_angle_in_rep <= 32.0:
                    alignment_score = 95.0
                elif self.max_torso_angle_in_rep <= 42.0:
                    alignment_score = 82.0
                else:
                    alignment_score = 58.0
                    self.active_feedback.append(
                        FeedbackEvent("form", FeedbackSeverity.WARNING, "Keep your chest upright")
                    )

                # Consistency Score (25%): 1.5s - 4.2s is ideal
                if 1.5 <= duration <= 4.2:
                    consistency_score = 95.0
                elif duration < 1.5:
                    consistency_score = 72.0
                    self.active_feedback.append(
                        FeedbackEvent("tempo", FeedbackSeverity.INFO, "Slow down your descent")
                    )
                else:
                    consistency_score = 80.0

                rep_form_score = (
                    0.40 * depth_score + 0.35 * alignment_score + 0.25 * consistency_score
                )

                completed_rep = RepResult(
                    rep_number=self.rep_count,
                    duration_seconds=duration,
                    form_score=rep_form_score,
                    depth_score=depth_score,
                    alignment_score=alignment_score,
                    consistency_score=consistency_score,
                    primary_feedback=primary_msg,
                    completed_at=now,
                )
                self.completed_reps.append(completed_rep)
                self.active_feedback.append(
                    FeedbackEvent("rep", FeedbackSeverity.GOOD, f"Rep {self.rep_count} complete! {primary_msg}")
                )

        elif self.current_phase == "COMPLETED":
            # Auto-reset to READY for the next repetition
            self.current_phase = "READY"
            self.min_knee_angle_in_rep = 180.0
            self.max_torso_angle_in_rep = 0.0

        # Real-time form coaching prompts during movement
        if torso_angle > 45.0 and self.current_phase in ["DESCENDING", "BOTTOM"]:
            self.active_feedback.append(
                FeedbackEvent("posture", FeedbackSeverity.WARNING, "Keep your chest up")
            )

        return AnalysisFrame(
            exercise=self.exercise_name,
            rep_count=self.rep_count,
            phase=self.current_phase,
            primary_angle=knee_angle,
            angles={
                "knee_angle": knee_angle,
                "hip_angle": hip_angle,
                "torso_angle": torso_angle,
            },
            form_score=self.get_average_form_score(),
            feedback=self.active_feedback,
            is_calibrated=True,
            calibration_message=None,
            rep_completed=rep_completed,
            completed_rep_details=completed_rep,
        )

    def reset(self):
        super().reset()
        self.min_knee_angle_in_rep = 180.0
        self.max_torso_angle_in_rep = 0.0
