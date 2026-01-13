from __future__ import annotations
import math
import numpy as np
from dataclasses import dataclass
from gosti.basic.aid import Number


@dataclass(frozen=True, slots=True)
class Vec2:
    """2D vector with plain floats (dimensionless).

    Use this for purely geometric / unitless math.
    If you need physical units (mm, m, ...), use Vector2D instead.
    """
    x: float
    y: float

    def as_np(self) -> np.ndarray:
        return np.array([self.x, self.y], dtype=float)

    def norm(self) -> float:
        return float(math.hypot(self.x, self.y))

    def normalized(self) -> Vec2:
        n = self.norm()
        if n == 0.0:
            raise ValueError("Cannot normalize zero vector.")
        return Vec2(self.x / n, self.y / n)

    def dot(self, other: Vec2) -> float:
        return self.x * other.x + self.y * other.y

    def cross_z(self, other: Vec2) -> float:
        """2D 'cross product' returning the z-component (scalar)."""
        return self.x * other.y - self.y * other.x

    def perp_ccw(self) -> Vec2:
        """Rotate by +90° (CCW): (x,y) -> (-y, x)."""
        return Vec2(-self.y, self.x)

    def __add__(self, other: Vec2) -> Vec2:
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vec2) -> Vec2:
        return Vec2(self.x - other.x, self.y - other.y)

    def __neg__(self) -> Vec2:
        return Vec2(-self.x, -self.y)

    def __mul__(self, k: Number) -> Vec2:
        return Vec2(self.x * float(k), self.y * float(k))

    def __rmul__(self, k: Number) -> Vec2:
        return self.__mul__(k)

    def __truediv__(self, k: Number) -> Vec2:
        kk = float(k)
        if kk == 0.0:
            raise ZeroDivisionError("Division by zero.")
        return Vec2(self.x / kk, self.y / kk)

    def __str__(self) -> str:
        return f"Vec2({self.x:.6g}, {self.y:.6g})"
