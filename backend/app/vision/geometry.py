"""Biomechanical geometry and vector calculations for pose analysis."""

from dataclasses import dataclass
from enum import IntEnum

import numpy as np


class PoseLandmark(IntEnum):
    """MediaPipe 33 pose landmark indices."""
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32


@dataclass
class Point3D:
    x: float
    y: float
    z: float = 0.0
    visibility: float = 1.0
    presence: float = 1.0

    def to_array_2d(self) -> np.ndarray:
        return np.array([self.x, self.y], dtype=np.float64)

    def to_array_3d(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z], dtype=np.float64)


def calculate_angle(
    a: Point3D | tuple[float, float] | np.ndarray,
    b: Point3D | tuple[float, float] | np.ndarray,
    c: Point3D | tuple[float, float] | np.ndarray,
    use_3d: bool = False,
) -> float:
    """Calculate the interior angle ABC in degrees at vertex point B.

    Args:
        a: First endpoint
        b: Middle vertex point
        c: Second endpoint
        use_3d: If True and 3D data exists, calculates 3D angle.

    Returns:
        Angle in degrees [0.0, 180.0]. Returns 0.0 if vectors are degenerate.
    """
    def _to_np(p: Point3D | tuple[float, float] | np.ndarray) -> np.ndarray:
        if isinstance(p, Point3D):
            return p.to_array_3d() if use_3d else p.to_array_2d()
        if isinstance(p, (tuple, list)):
            return np.array(p[:3] if use_3d else p[:2], dtype=np.float64)
        return np.asarray(p, dtype=np.float64)

    pt_a = _to_np(a)
    pt_b = _to_np(b)
    pt_c = _to_np(c)

    vec_ba = pt_a - pt_b
    vec_bc = pt_c - pt_b

    norm_ba = np.linalg.norm(vec_ba)
    norm_bc = np.linalg.norm(vec_bc)

    # Prevent division by zero if points coincide
    if norm_ba < 1e-7 or norm_bc < 1e-7:
        return 0.0

    cos_theta = np.dot(vec_ba, vec_bc) / (norm_ba * norm_bc)
    # Clip numerical precision drift
    cos_theta = np.clip(cos_theta, -1.0, 1.0)

    angle_rad = np.arccos(cos_theta)
    return float(np.degrees(angle_rad))


def calculate_vertical_angle(
    top: Point3D | tuple[float, float],
    bottom: Point3D | tuple[float, float],
) -> float:
    """Calculate angle of a segment (e.g. torso, shin) relative to the vertical axis (downward Y).

    In image coordinates, Y increases downward.
    A perfectly vertical upright torso (top.y < bottom.y, top.x == bottom.x) has angle 0°.
    Leaning forward or backward increases the angle toward 90°.
    """
    x1, y1 = (top.x, top.y) if isinstance(top, Point3D) else (top[0], top[1])
    x2, y2 = (bottom.x, bottom.y) if isinstance(bottom, Point3D) else (bottom[0], bottom[1])

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    if dy < 1e-7:
        return 90.0  # Horizontal segment

    # Angle relative to vertical line
    angle_rad = np.arctan2(dx, dy)
    return float(np.degrees(angle_rad))


def distance_2d(
    a: Point3D | tuple[float, float],
    b: Point3D | tuple[float, float],
) -> float:
    """Calculate 2D Euclidean distance between two points."""
    x1, y1 = (a.x, a.y) if isinstance(a, Point3D) else (a[0], a[1])
    x2, y2 = (b.x, b.y) if isinstance(b, Point3D) else (b[0], b[1])
    return float(np.hypot(x2 - x1, y2 - y1))


def midpoint_2d(
    a: Point3D | tuple[float, float],
    b: Point3D | tuple[float, float],
) -> Point3D:
    """Compute 2D midpoint between two points."""
    x1, y1 = (a.x, a.y) if isinstance(a, Point3D) else (a[0], a[1])
    x2, y2 = (b.x, b.y) if isinstance(b, Point3D) else (b[0], b[1])
    v1 = getattr(a, "visibility", 1.0)
    v2 = getattr(b, "visibility", 1.0)
    return Point3D(
        x=(x1 + x2) / 2.0,
        y=(y1 + y2) / 2.0,
        z=0.0,
        visibility=min(v1, v2),
    )


def are_landmarks_visible(
    landmarks: dict[int, Point3D],
    required_indices: list[int],
    min_visibility: float = 0.60,
) -> tuple[bool, list[int]]:
    """Check if all required landmarks exist and meet the visibility threshold.

    Returns:
        (all_visible: bool, missing_or_low_confidence_indices: List[int])
    """
    missing = []
    for idx in required_indices:
        point = landmarks.get(idx)
        if point is None or point.visibility < min_visibility:
            missing.append(idx)
    return (len(missing) == 0, missing)
