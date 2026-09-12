"""Tests for biomechanical geometry module."""

import pytest
from app.vision.geometry import (
    Point3D,
    are_landmarks_visible,
    calculate_angle,
    calculate_vertical_angle,
    distance_2d,
    midpoint_2d,
)


def test_calculate_angle_right_angle():
    a = (0.0, 1.0)
    b = (0.0, 0.0)
    c = (1.0, 0.0)
    angle = calculate_angle(a, b, c)
    assert pytest.approx(angle, 0.1) == 90.0


def test_calculate_angle_straight_line():
    a = (0.0, 1.0)
    b = (0.0, 0.0)
    c = (0.0, -1.0)
    angle = calculate_angle(a, b, c)
    assert pytest.approx(angle, 0.1) == 180.0


def test_calculate_angle_acute():
    a = (1.0, 1.0)
    b = (0.0, 0.0)
    c = (1.0, 0.0)
    angle = calculate_angle(a, b, c)
    assert pytest.approx(angle, 0.1) == 45.0


def test_calculate_angle_point3d():
    p1 = Point3D(0.0, 1.0, 0.0)
    p2 = Point3D(0.0, 0.0, 0.0)
    p3 = Point3D(1.0, 0.0, 0.0)
    angle = calculate_angle(p1, p2, p3)
    assert pytest.approx(angle, 0.1) == 90.0


def test_calculate_angle_degenerate():
    # Identical points should not crash and return 0.0
    p1 = Point3D(0.0, 0.0, 0.0)
    p2 = Point3D(0.0, 0.0, 0.0)
    p3 = Point3D(1.0, 0.0, 0.0)
    angle = calculate_angle(p1, p2, p3)
    assert angle == 0.0


def test_calculate_vertical_angle():
    # Perfectly vertical segment
    top = Point3D(0.5, 0.2)
    bottom = Point3D(0.5, 0.8)
    assert pytest.approx(calculate_vertical_angle(top, bottom), 0.1) == 0.0

    # 45 degree lean
    lean_top = Point3D(0.2, 0.2)
    lean_bottom = Point3D(0.5, 0.5)
    assert pytest.approx(calculate_vertical_angle(lean_top, lean_bottom), 0.5) == 45.0


def test_distance_and_midpoint():
    p1 = Point3D(0.0, 0.0)
    p2 = Point3D(3.0, 4.0)
    assert pytest.approx(distance_2d(p1, p2), 0.1) == 5.0

    mid = midpoint_2d(p1, p2)
    assert mid.x == 1.5
    assert mid.y == 2.0


def test_are_landmarks_visible():
    landmarks = {
        0: Point3D(0.5, 0.5, visibility=0.9),
        1: Point3D(0.5, 0.6, visibility=0.4),  # Low visibility
        2: Point3D(0.5, 0.7, visibility=0.8),
    }

    all_vis, missing = are_landmarks_visible(landmarks, [0, 2], min_visibility=0.6)
    assert all_vis is True
    assert len(missing) == 0

    all_vis_fail, missing_fail = are_landmarks_visible(landmarks, [0, 1, 2], min_visibility=0.6)
    assert all_vis_fail is False
    assert 1 in missing_fail
