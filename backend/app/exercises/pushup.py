"""Push-up exercise biomechanical analyzer and state machine."""

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
)


class PushupAnalyzer(ExerciseAnalyzer):
    """Biomechanical analyzer for push-ups.

    Tracks elbow flexion and shoulder-hip-ankle plank linearity.
    State Machine:
        TOP -> DESCENDING -> BOTTOM -> ASCENDING -> COMPLETED -> TOP
    """

    TOP_ELBOW_THRESHOLD = 155.0     # Full extension at top of plank
    DESCENDING_TRIGGER = 145.0      # Beginning of downward movement
    BOTTOM_TARGET = 90.0           # 90 degrees elbow bend for full chest depth
    SHALLOW_THRESHOLD = 110.0      # Cutoff for valid rep
    ASCENDING_TRIGGER = 105.0      # Pressing up

    def __init__(self):
        super().__init__(exercise_name="pushup")
        self.min_elbow_in_rep = 180.0
        self.min_plank_angle_in_rep = 180.0
        self.preferred_side = "right"

    def get_required_landmarks(self) -> list[int]:
        return [
            PoseLandmark.LEFT_SHOULDER,
            PoseLandmark.LEFT_ELBOW,
            PoseLandmark.LEFT_WRIST,
            PoseLandmark.LEFT_HIP,
            PoseLandmark.LEFT_ANKLE,
            PoseLandmark.RIGHT_SHOULDER,
            PoseLandmark.RIGHT_ELBOW,
            PoseLandmark.RIGHT_WRIST,
            PoseLandmark.RIGHT_HIP,
            PoseLandmark.RIGHT_ANKLE,
        ]

    def _determine_active_side(self, landmarks: dict[int, Point3D]) -> str:
        left_lms = [
            landmarks.get(PoseLandmark.LEFT_SHOULDER),
            landmarks.get(PoseLandmark.LEFT_ELBOW),
            landmarks.get(PoseLandmark.LEFT_WRIST),
            landmarks.get(PoseLandmark.LEFT_HIP),
        ]
        right_lms = [
            landmarks.get(PoseLandmark.RIGHT_SHOULDER),
            landmarks.get(PoseLandmark.RIGHT_ELBOW),
            landmarks.get(PoseLandmark.RIGHT_WRIST),
            landmarks.get(PoseLandmark.RIGHT_HIP),
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

        side = self._determine_active_side(landmarks)
        self.preferred_side = side

        if side == "left":
            shld_idx = PoseLandmark.LEFT_SHOULDER
            elbw_idx = PoseLandmark.LEFT_ELBOW
            wrst_idx = PoseLandmark.LEFT_WRIST
            hip_idx = PoseLandmark.LEFT_HIP
            ankl_idx = PoseLandmark.LEFT_ANKLE
        else:
            shld_idx = PoseLandmark.RIGHT_SHOULDER
            elbw_idx = PoseLandmark.RIGHT_ELBOW
            wrst_idx = PoseLandmark.RIGHT_WRIST
            hip_idx = PoseLandmark.RIGHT_HIP
            ankl_idx = PoseLandmark.RIGHT_ANKLE

        req_indices = [shld_idx, elbw_idx, wrst_idx, hip_idx, ankl_idx]
        visible, _ = are_landmarks_visible(landmarks, req_indices, min_visibility=0.50)

        if not visible:
            calib_msg = "Ensure arm and torso are visible in plank position"
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
        elbow = landmarks[elbw_idx]
        wrist = landmarks[wrst_idx]
        hip = landmarks[hip_idx]
        ankle = landmarks[ankl_idx]

        # Angles
        elbow_angle = calculate_angle(shoulder, elbow, wrist)
        plank_angle = calculate_angle(shoulder, hip, ankle)

        rep_completed = False
        completed_rep: RepResult | None = None

        # State Machine Transitions
        if self.current_phase in ["READY", "TOP"]:
            self.min_elbow_in_rep = 180.0
            self.min_plank_angle_in_rep = 180.0

            if elbow_angle <= self.DESCENDING_TRIGGER:
                self.current_phase = "DESCENDING"
                self.rep_start_time = now
                self.min_elbow_in_rep = elbow_angle
                self.min_plank_angle_in_rep = plank_angle

        elif self.current_phase == "DESCENDING":
            self.min_elbow_in_rep = min(self.min_elbow_in_rep, elbow_angle)
            self.min_plank_angle_in_rep = min(self.min_plank_angle_in_rep, plank_angle)

            if elbow_angle <= self.BOTTOM_TARGET:
                self.current_phase = "BOTTOM"
                self.active_feedback.append(
                    FeedbackEvent("depth", FeedbackSeverity.GOOD, "Good push-up depth!")
                )
            elif elbow_angle > self.min_elbow_in_rep + 8.0:
                if self.min_elbow_in_rep <= self.SHALLOW_THRESHOLD:
                    self.current_phase = "ASCENDING"
                else:
                    self.current_phase = "TOP"
                    self.active_feedback.append(
                        FeedbackEvent("depth", FeedbackSeverity.WARNING, "Lower your chest further")
                    )

        elif self.current_phase == "BOTTOM":
            self.min_elbow_in_rep = min(self.min_elbow_in_rep, elbow_angle)
            self.min_plank_angle_in_rep = min(self.min_plank_angle_in_rep, plank_angle)

            if elbow_angle > self.min_elbow_in_rep + 6.0:
                self.current_phase = "ASCENDING"

        elif self.current_phase == "ASCENDING":
            self.min_plank_angle_in_rep = min(self.min_plank_angle_in_rep, plank_angle)

            if elbow_angle >= self.TOP_ELBOW_THRESHOLD:
                self.current_phase = "COMPLETED"
                self.rep_count += 1
                rep_completed = True

                duration = max(now - (self.rep_start_time or now), 0.5)

                # Depth score
                if self.min_elbow_in_rep <= 88.0:
                    depth_score = 100.0
                    primary_msg = "Full range of motion"
                elif self.min_elbow_in_rep <= 98.0:
                    depth_score = 88.0
                    primary_msg = "Good chest depth"
                elif self.min_elbow_in_rep <= 110.0:
                    depth_score = 65.0
                    primary_msg = "Partial rep"
                else:
                    depth_score = 40.0
                    primary_msg = "Lower chest further"

                # Plank alignment score (Shoulder-Hip-Ankle)
                if 160.0 <= self.min_plank_angle_in_rep <= 180.0:
                    alignment_score = 95.0
                elif 145.0 <= self.min_plank_angle_in_rep < 160.0:
                    alignment_score = 75.0
                    self.active_feedback.append(
                        FeedbackEvent("form", FeedbackSeverity.WARNING, "Keep hips aligned - avoid sagging")
                    )
                else:
                    alignment_score = 55.0
                    self.active_feedback.append(
                        FeedbackEvent("form", FeedbackSeverity.WARNING, "Engage core to maintain straight line")
                    )

                # Consistency
                if 1.2 <= duration <= 3.8:
                    consistency_score = 95.0
                else:
                    consistency_score = 78.0

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
            self.current_phase = "TOP"
            self.min_elbow_in_rep = 180.0
            self.min_plank_angle_in_rep = 180.0

        # Real-time plank warning
        if plank_angle < 150.0:
            self.active_feedback.append(
                FeedbackEvent("plank", FeedbackSeverity.WARNING, "Hips sagging - engage your core")
            )

        return AnalysisFrame(
            exercise=self.exercise_name,
            rep_count=self.rep_count,
            phase=self.current_phase,
            primary_angle=elbow_angle,
            angles={
                "elbow_angle": elbow_angle,
                "plank_angle": plank_angle,
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
        self.min_elbow_in_rep = 180.0
        self.min_plank_angle_in_rep = 180.0
