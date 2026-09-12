"""Tests for landmark smoothing filters."""

import pytest
from app.vision.geometry import Point3D
from app.vision.smoothing import EMAPointFilter, LandmarkSmoother, OneEuroFilterPoint


def test_ema_filter_reduces_jitter():
    filt = EMAPointFilter(alpha=0.5)

    # First point initializes filter
    p1 = filt.filter(Point3D(10.0, 10.0, 0.0))
    assert p1.x == 10.0

    # Large step change smoothed by 50%
    p2 = filt.filter(Point3D(20.0, 20.0, 0.0))
    assert p2.x == 15.0
    assert p2.y == 15.0

    # Further step
    p3 = filt.filter(Point3D(20.0, 20.0, 0.0))
    assert p3.x == 17.5


def test_one_euro_filter():
    filt = OneEuroFilterPoint(min_cutoff=1.0, beta=0.01)

    t = 0.0
    pt = Point3D(5.0, 5.0, 0.0)
    out1 = filt.filter(pt, timestamp=t)
    assert out1.x == 5.0

    # Small jitter at low velocity -> heavily smoothed
    t += 0.033
    out2 = filt.filter(Point3D(5.1, 4.9, 0.0), timestamp=t)
    assert abs(out2.x - 5.0) < 0.08


def test_landmark_smoother_multi_point():
    smoother = LandmarkSmoother(method="ema", alpha=0.7)

    lms = {
        0: Point3D(1.0, 1.0),
        1: Point3D(2.0, 2.0),
    }

    res1 = smoother.smooth(lms)
    assert res1[0].x == 1.0

    lms2 = {
        0: Point3D(2.0, 2.0),
        1: Point3D(3.0, 3.0),
    }
    res2 = smoother.smooth(lms2)
    # 0.7 * 2.0 + 0.3 * 1.0 = 1.7
    assert pytest.approx(res2[0].x, 0.01) == 1.7
