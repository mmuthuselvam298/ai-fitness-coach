"""Demo mode service for synthetic kinematics and sample video generation."""

import math
import os

import cv2
import numpy as np
from app.vision.geometry import Point3D, PoseLandmark


class DemoService:
    @staticmethod
    def generate_squat_landmarks_sequence(num_reps: int = 3, fps: int = 30) -> list[dict[int, Point3D]]:
        """Generates a realistic biomechanical sequence of landmarks for squats."""
        frames: list[dict[int, Point3D]] = []
        frames_per_rep = fps * 3  # 3 seconds per rep (1.5s down, 1.5s up)

        for r in range(num_reps):
            for i in range(frames_per_rep):
                # Phase parameter t in [0, 2*pi]
                phase = (i / frames_per_rep) * 2.0 * math.pi
                # Invert cosine so it starts at 0, dips to -1 at half rep, returns to 0
                depth_factor = (1.0 - math.cos(phase)) / 2.0  # 0.0 at top, 1.0 at bottom

                # Kinematic positions for realistic 175 deg -> 85 deg squat
                hip_y = 0.45 + 0.26 * depth_factor
                hip_x = 0.50 - 0.12 * depth_factor

                knee_y = 0.70 + 0.02 * depth_factor
                knee_x = 0.52 + 0.04 * depth_factor

                ankle_y = 0.90
                ankle_x = 0.50

                shoulder_y = 0.20 + 0.22 * depth_factor
                shoulder_x = 0.48 - 0.05 * depth_factor

                lms = {
                    PoseLandmark.NOSE: Point3D(shoulder_x, shoulder_y - 0.10, 0.0, 0.99),
                    PoseLandmark.RIGHT_SHOULDER: Point3D(shoulder_x, shoulder_y, 0.0, 0.98),
                    PoseLandmark.LEFT_SHOULDER: Point3D(shoulder_x, shoulder_y, 0.0, 0.90),
                    PoseLandmark.RIGHT_ELBOW: Point3D(shoulder_x + 0.08, shoulder_y + 0.10, 0.0, 0.95),
                    PoseLandmark.RIGHT_WRIST: Point3D(shoulder_x + 0.12, shoulder_y + 0.05, 0.0, 0.95),
                    PoseLandmark.RIGHT_HIP: Point3D(hip_x, hip_y, 0.0, 0.98),
                    PoseLandmark.LEFT_HIP: Point3D(hip_x, hip_y, 0.0, 0.90),
                    PoseLandmark.RIGHT_KNEE: Point3D(knee_x, knee_y, 0.0, 0.98),
                    PoseLandmark.LEFT_KNEE: Point3D(knee_x, knee_y, 0.0, 0.90),
                    PoseLandmark.RIGHT_ANKLE: Point3D(ankle_x, ankle_y, 0.0, 0.98),
                    PoseLandmark.LEFT_ANKLE: Point3D(ankle_x, ankle_y, 0.0, 0.90),
                }
                frames.append(lms)
        return frames

    @staticmethod
    def generate_pushup_landmarks_sequence(num_reps: int = 3, fps: int = 30) -> list[dict[int, Point3D]]:
        """Generates synthetic landmarks for push-ups."""
        frames: list[dict[int, Point3D]] = []
        frames_per_rep = fps * 3

        for r in range(num_reps):
            for i in range(frames_per_rep):
                phase = (i / frames_per_rep) * 2.0 * math.pi
                depth = (1.0 - math.cos(phase)) / 2.0  # 0 at plank, 1 at bottom

                # Straight line at top: shoulder (0.70, 0.48), elbow (0.70, 0.62), wrist (0.70, 0.76)
                # At bottom: shoulder drops to 0.64, elbow bends back to (0.58, 0.68)
                wrist_x, wrist_y = 0.70, 0.76
                shoulder_y = 0.48 + 0.16 * depth
                shoulder_x = 0.70
                elbow_x = 0.70 - 0.12 * depth
                elbow_y = 0.62 + 0.06 * depth

                ankle_x, ankle_y = 0.20, 0.76
                hip_x, hip_y = 0.45, 0.62 + 0.14 * depth

                lms = {
                    PoseLandmark.NOSE: Point3D(shoulder_x + 0.08, shoulder_y - 0.04, 0.0, 0.99),
                    PoseLandmark.RIGHT_SHOULDER: Point3D(shoulder_x, shoulder_y, 0.0, 0.98),
                    PoseLandmark.LEFT_SHOULDER: Point3D(shoulder_x, shoulder_y, 0.0, 0.90),
                    PoseLandmark.RIGHT_ELBOW: Point3D(elbow_x, elbow_y, 0.0, 0.98),
                    PoseLandmark.RIGHT_WRIST: Point3D(wrist_x, wrist_y, 0.0, 0.98),
                    PoseLandmark.RIGHT_HIP: Point3D(hip_x, hip_y, 0.0, 0.98),
                    PoseLandmark.LEFT_HIP: Point3D(hip_x, hip_y, 0.0, 0.90),
                    PoseLandmark.RIGHT_KNEE: Point3D(0.32, 0.68 + 0.07 * depth, 0.0, 0.95),
                    PoseLandmark.RIGHT_ANKLE: Point3D(ankle_x, ankle_y, 0.0, 0.98),
                }
                frames.append(lms)
        return frames

    @staticmethod
    def generate_bicep_curl_landmarks_sequence(num_reps: int = 3, fps: int = 30) -> list[dict[int, Point3D]]:
        """Generates synthetic landmarks for bicep curls."""
        frames: list[dict[int, Point3D]] = []
        frames_per_rep = fps * 3

        for r in range(num_reps):
            for i in range(frames_per_rep):
                phase = (i / frames_per_rep) * 2.0 * math.pi
                curl_progress = (1.0 - math.cos(phase)) / 2.0  # 0 at bottom, 1 at peak

                shoulder_x, shoulder_y = 0.50, 0.30
                elbow_x, elbow_y = 0.50, 0.50  # Stable elbow
                # Wrist swings from extended down (0.50, 0.70) to curled up (0.50, 0.34)
                wrist_angle = math.pi / 2.0 - curl_progress * (math.pi * 0.75)
                wrist_len = 0.20
                wrist_x = elbow_x + wrist_len * math.cos(wrist_angle)
                wrist_y = elbow_y + wrist_len * math.sin(wrist_angle)

                lms = {
                    PoseLandmark.NOSE: Point3D(0.50, 0.18, 0.0, 0.99),
                    PoseLandmark.RIGHT_SHOULDER: Point3D(shoulder_x, shoulder_y, 0.0, 0.98),
                    PoseLandmark.LEFT_SHOULDER: Point3D(shoulder_x, shoulder_y, 0.0, 0.90),
                    PoseLandmark.RIGHT_ELBOW: Point3D(elbow_x, elbow_y, 0.0, 0.98),
                    PoseLandmark.RIGHT_WRIST: Point3D(wrist_x, wrist_y, 0.0, 0.98),
                    PoseLandmark.RIGHT_HIP: Point3D(0.50, 0.60, 0.0, 0.98),
                    PoseLandmark.RIGHT_KNEE: Point3D(0.50, 0.78, 0.0, 0.95),
                    PoseLandmark.RIGHT_ANKLE: Point3D(0.50, 0.95, 0.0, 0.95),
                }
                frames.append(lms)
        return frames

    @classmethod
    def render_demo_video(cls, exercise: str, output_path: str, width: int = 640, height: int = 480) -> str:
        """Renders an aesthetic animated demo video with human silhouette and exercise movement."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        if exercise == "pushup":
            seq = cls.generate_pushup_landmarks_sequence(num_reps=3, fps=30)
        elif exercise == "bicep_curl":
            seq = cls.generate_bicep_curl_landmarks_sequence(num_reps=3, fps=30)
        else:
            seq = cls.generate_squat_landmarks_sequence(num_reps=3, fps=30)

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_path, fourcc, 30.0, (width, height))

        for frame_idx, lms in enumerate(seq):
            # Clean studio background: Warm light off-white (249, 251, 251) in BGR (251, 251, 249)
            img = np.full((height, width, 3), (249, 251, 251), dtype=np.uint8)

            # Minimal subtle grid lines
            for y in range(80, height, 80):
                cv2.line(img, (0, y), (width, y), (235, 237, 237), 1)

            # Ground shadow / floor line
            cv2.line(img, (40, int(height * 0.92)), (width - 40, int(height * 0.92)), (210, 215, 215), 2)

            # Draw limbs as sleek athletic silhouettes
            connections = [
                (PoseLandmark.RIGHT_SHOULDER, PoseLandmark.RIGHT_ELBOW),
                (PoseLandmark.RIGHT_ELBOW, PoseLandmark.RIGHT_WRIST),
                (PoseLandmark.RIGHT_SHOULDER, PoseLandmark.RIGHT_HIP),
                (PoseLandmark.RIGHT_HIP, PoseLandmark.RIGHT_KNEE),
                (PoseLandmark.RIGHT_KNEE, PoseLandmark.RIGHT_ANKLE),
            ]

            # Charcoal tone for body limbs
            body_color = (45, 42, 38)
            for p1, p2 in connections:
                if p1 in lms and p2 in lms:
                    pt1 = (int(lms[p1].x * width), int(lms[p1].y * height))
                    pt2 = (int(lms[p2].x * width), int(lms[p2].y * height))
                    cv2.line(img, pt1, pt2, body_color, 8, cv2.LINE_AA)

            # Draw joints
            for idx, pt in lms.items():
                cx, cy = int(pt.x * width), int(pt.y * height)
                cv2.circle(img, (cx, cy), 7, (255, 255, 255), -1, cv2.LINE_AA)
                # Fresh green accent joint
                cv2.circle(img, (cx, cy), 5, (129, 185, 16), -1, cv2.LINE_AA)

            # Draw head
            if PoseLandmark.NOSE in lms:
                head_pt = (int(lms[PoseLandmark.NOSE].x * width), int(lms[PoseLandmark.NOSE].y * height))
                cv2.circle(img, head_pt, 16, body_color, -1, cv2.LINE_AA)

            # Demo watermark tag
            cv2.putText(
                img,
                f"FORMFIT AI DEMO - {exercise.upper()} SYNTHETIC TEST CLIP",
                (25, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (120, 120, 120),
                1,
                cv2.LINE_AA,
            )

            out.write(img)

        out.release()
        return output_path
