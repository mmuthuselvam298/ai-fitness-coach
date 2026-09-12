"""Bicep curl exercise biomechanical analyzer and state machine."""

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


class BicepCurlAnalyzer(ExerciseAnalyzer):
    """Biomechanical analyzer for bicep curls.

    Tracks elbow flexion and upper-arm stability (elbow flare / swinging).
    State Machine:
        EXTENDED -> CURLING -> CONTRACTED -> RETURNING -> COMPLETED -> EXTENDED
    """

    EXTENDED_THRESHOLD = 150.0   # Arm extended down
    CURLING_TRIGGER = 140.0      # Beginning of curl
    CONTRACTED_TARGET = 55.0     # Peak flexion at top
    SHALLOW_THRESHOLD = 75.0     # Max peak angle to qualify as rep
    RETURNING_TRIGGER = 70.0     # Lowering arm

    def __init__(self):
        super().__init__(exercise_name="bicep_curl")
        self.min_elbow_in_rep = 180.0
        self.max_upper_arm_drift = 0.0
        self.preferred_side = "right"

    def get_required_landmarks(self) -> list[int]:
        return [
            PoseLandmark.LEFT_SHOULDER,
            PoseLandmark.LEFT_ELBOW,
            PoseLandmark.LEFT_WRIST,
            PoseLandmark.LEFT_HIP,
            PoseLandmark.RIGHT_SHOULDER,
            PoseLandmark.RIGHT_ELBOW,
            PoseLandmark.RIGHT_WRIST,
            PoseLandmark.RIGHT_HIP,
        ]

    def _determine_active_side(self, landmarks: dict[int, Point3D]) -> str:
        left_lms = [
            landmarks.get(PoseLandmark.LEFT_SHOULDER),
            landmarks.get(PoseLandmark.LEFT_ELBOW),
            landmarks.get(PoseLandmark.LEFT_WRIST),
        ]
        right_lms = [
            landmarks.get(PoseLandmark.RIGHT_SHOULDER),
            landmarks.get(PoseLandmark.RIGHT_ELBOW),
            landmarks.get(PoseLandmark.RIGHT_WRIST),
        ]

        left_vis = (
            sum(p.visibility for p in left_lms if p is not None) / 3.0
            if all(p is not None for p in left_lms)
            else 0.0
        )
        right_vis = (
            sum(p.visibility for p in right_lms if p is not None) / 3.0
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
        else:
            shld_idx = PoseLandmark.RIGHT_SHOULDER
            elbw_idx = PoseLandmark.RIGHT_ELBOW
            wrst_idx = PoseLandmark.RIGHT_WRIST
            hip_idx = PoseLandmark.RIGHT_HIP

        req_indices = [shld_idx, elbw_idx, wrst_idx, hip_idx]
        visible, _ = are_landmarks_visible(landmarks, req_indices, min_visibility=0.55)

        if not visible:
            calib_msg = "Ensure arm and torso are visible"
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

        # Angles
        elbow_angle = calculate_angle(shoulder, elbow, wrist)
        upper_arm_angle = calculate_angle(hip, shoulder, elbow)

        rep_completed = False
        completed_rep: RepResult | None = None

        # State machine
        if self.current_phase in ["READY", "EXTENDED"]:
            self.min_elbow_in_rep = 180.0
            self.max_upper_arm_drift = 0.0

            if elbow_angle <= self.CURLING_TRIGGER:
                self.current_phase = "CURLING"
                self.rep_start_time = now
                self.min_elbow_in_rep = elbow_angle

        elif self.current_phase == "CURLING":
            self.min_elbow_in_rep = min(self.min_elbow_in_rep, elbow_angle)
            self.max_upper_arm_drift = max(self.max_upper_arm_drift, upper_arm_angle)

            if elbow_angle <= self.CONTRACTED_TARGET:
                self.current_phase = "CONTRACTED"
                self.active_feedback.append(
                    FeedbackEvent("contraction", FeedbackSeverity.GOOD, "Good peak contraction!")
                )
            elif elbow_angle > self.min_elbow_in_rep + 8.0:
                if self.min_elbow_in_rep <= self.SHALLOW_THRESHOLD:
                    self.current_phase = "RETURNING"
                else:
                    self.current_phase = "EXTENDED"
                    self.active_feedback.append(
                        FeedbackEvent("rom", FeedbackSeverity.WARNING, "Curl all the way up")
                    )

        elif self.current_phase == "CONTRACTED":
            self.min_elbow_in_rep = min(self.min_elbow_in_rep, elbow_angle)
            self.max_upper_arm_drift = max(self.max_upper_arm_drift, upper_arm_angle)

            if elbow_angle > self.min_elbow_in_rep + 6.0:
                self.current_phase = "RETURNING"

        elif self.current_phase == "RETURNING":
            self.max_upper_arm_drift = max(self.max_upper_arm_drift, upper_arm_angle)

            if elbow_angle >= self.EXTENDED_THRESHOLD:
                self.current_phase = "COMPLETED"
                self.rep_count += 1
                rep_completed = True

                duration = max(now - (self.rep_start_time or now), 0.5)

                # Contraction Depth score
                if self.min_elbow_in_rep <= 50.0:
                    depth_score = 100.0
                    primary_msg = "Full range of motion"
                elif self.min_elbow_in_rep <= 60.0:
                    depth_score = 88.0
                    primary_msg = "Good curl contraction"
                elif self.min_elbow_in_rep <= 75.0:
                    depth_score = 65.0
                    primary_msg = "Incomplete contraction"
                else:
                    depth_score = 40.0
                    primary_msg = "Curl higher"

                # Upper-arm stability score (drift <= 18 degrees is good)
                if self.max_upper_arm_drift <= 20.0:
                    alignment_score = 95.0
                elif self.max_upper_arm_drift <= 30.0:
                    alignment_score = 78.0
                    self.active_feedback.append(
                        FeedbackEvent("stability", FeedbackSeverity.WARNING, "Keep elbow pinned to side")
                    )
                else:
                    alignment_score = 55.0
                    self.active_feedback.append(
                        FeedbackEvent("stability", FeedbackSeverity.WARNING, "Avoid swinging elbow")
                    )

                # Tempo
                if 1.0 <= duration <= 3.5:
                    consistency_score = 95.0
                else:
                    consistency_score = 75.0

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
            self.current_phase = "EXTENDED"
            self.min_elbow_in_rep = 180.0
            self.max_upper_arm_drift = 0.0

        # Stability warning during curl
        if upper_arm_angle > 30.0 and self.current_phase in ["CURLING", "CONTRACTED"]:
            self.active_feedback.append(
                FeedbackEvent("form", FeedbackSeverity.WARNING, "Keep elbow pinned to your side")
            )

        return AnalysisFrame(
            exercise=self.exercise_name,
            rep_count=self.rep_count,
            phase=self.current_phase,
            primary_angle=elbow_angle,
            angles={
                "elbow_angle": elbow_angle,
                "upper_arm_drift": upper_arm_angle,
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
        self.max_upper_arm_drift = 0.0
