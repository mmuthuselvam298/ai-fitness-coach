"""Landmark smoothing mechanisms for noise reduction and jitter prevention."""

import math
import time
from typing import Union

from app.vision.geometry import Point3D


class LowPassFilter:
    """Standard first-order low-pass filter."""

    def __init__(self, alpha: float):
        self._alpha = alpha
        self._s: float | None = None

    def filter(self, value: float, alpha: float | None = None) -> float:
        a = alpha if alpha is not None else self._alpha
        if self._s is None:
            self._s = value
        else:
            self._s = a * value + (1.0 - a) * self._s
        return self._s

    def reset(self):
        self._s = None


class OneEuroFilter1D:
    """1D One Euro Filter for adaptive frequency noise suppression with minimal lag.

    Based on Casiez et al., CHI 2012:
    Adapts cutoff frequency based on velocity to balance jitter removal vs lag.
    """

    def __init__(
        self,
        min_cutoff: float = 1.0,
        beta: float = 0.007,
        d_cutoff: float = 1.0,
    ):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.x_filter = LowPassFilter(self._alpha(min_cutoff, 1.0 / 30.0))
        self.dx_filter = LowPassFilter(self._alpha(d_cutoff, 1.0 / 30.0))
        self.prev_time: float | None = None
        self.prev_x: float | None = None

    @staticmethod
    def _alpha(cutoff: float, dt: float) -> float:
        tau = 1.0 / (2.0 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)

    def filter(self, x: float, timestamp: float | None = None) -> float:
        now = timestamp if timestamp is not None else time.time()
        if self.prev_time is None:
            self.prev_time = now
            self.prev_x = x
            return self.x_filter.filter(x)

        dt = max(now - self.prev_time, 1e-4)
        self.prev_time = now

        # Compute rate of change (derivative)
        dx = (x - self.prev_x) / dt if self.prev_x is not None else 0.0
        self.prev_x = x

        edx = self.dx_filter.filter(dx, self._alpha(self.d_cutoff, dt))
        cutoff = self.min_cutoff + self.beta * abs(edx)
        return self.x_filter.filter(x, self._alpha(cutoff, dt))

    def reset(self):
        self.prev_time = None
        self.prev_x = None
        self.x_filter.reset()
        self.dx_filter.reset()


class OneEuroFilterPoint:
    def __init__(self, min_cutoff: float = 1.0, beta: float = 0.007):
        self.fx = OneEuroFilter1D(min_cutoff, beta)
        self.fy = OneEuroFilter1D(min_cutoff, beta)
        self.fz = OneEuroFilter1D(min_cutoff, beta)

    def filter(self, point: Point3D, timestamp: float | None = None) -> Point3D:
        return Point3D(
            x=self.fx.filter(point.x, timestamp),
            y=self.fy.filter(point.y, timestamp),
            z=self.fz.filter(point.z, timestamp),
            visibility=point.visibility,
            presence=point.presence,
        )

    def reset(self):
        self.fx.reset()
        self.fy.reset()
        self.fz.reset()


class EMAPointFilter:
    """Exponential Moving Average filter for 3D landmarks."""

    def __init__(self, alpha: float = 0.65):
        self.alpha = max(0.01, min(1.0, alpha))
        self.prev_point: Point3D | None = None

    def filter(self, point: Point3D) -> Point3D:
        if self.prev_point is None:
            self.prev_point = point
            return point

        # Filter coordinates
        new_x = self.alpha * point.x + (1.0 - self.alpha) * self.prev_point.x
        new_y = self.alpha * point.y + (1.0 - self.alpha) * self.prev_point.y
        new_z = self.alpha * point.z + (1.0 - self.alpha) * self.prev_point.z

        smoothed = Point3D(
            x=new_x,
            y=new_y,
            z=new_z,
            visibility=point.visibility,
            presence=point.presence,
        )
        self.prev_point = smoothed
        return smoothed

    def reset(self):
        self.prev_point = None


class LandmarkSmoother:
    """Unified smoother managing coordinate filters for all 33 pose landmarks."""

    def __init__(
        self,
        method: str = "ema",
        alpha: float = 0.65,
        one_euro_min_cutoff: float = 1.0,
        one_euro_beta: float = 0.007,
    ):
        self.method = method.lower()
        self.alpha = alpha
        self.one_euro_min_cutoff = one_euro_min_cutoff
        self.one_euro_beta = one_euro_beta
        self.filters: dict[int, Union[EMAPointFilter, OneEuroFilterPoint]] = {}

    def smooth(
        self,
        landmarks: dict[int, Point3D],
        timestamp: float | None = None,
    ) -> dict[int, Point3D]:
        """Smooths noisy landmarks in-place or returns stabilized dictionary."""
        smoothed: dict[int, Point3D] = {}
        for idx, point in landmarks.items():
            if idx not in self.filters:
                if self.method == "one_euro":
                    self.filters[idx] = OneEuroFilterPoint(
                        self.one_euro_min_cutoff, self.one_euro_beta
                    )
                else:
                    self.filters[idx] = EMAPointFilter(self.alpha)

            f = self.filters[idx]
            if isinstance(f, OneEuroFilterPoint):
                smoothed[idx] = f.filter(point, timestamp)
            else:
                smoothed[idx] = f.filter(point)
        return smoothed

    def reset(self):
        for f in self.filters.values():
            f.reset()
        self.filters.clear()
