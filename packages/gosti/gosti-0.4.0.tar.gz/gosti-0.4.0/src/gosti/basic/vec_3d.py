from __future__ import annotations
import math
import numpy as np
from dataclasses import dataclass
from gosti.basic.aid import Number



@dataclass(frozen=True, slots=True)
class Vec3:
    """3D vector with plain floats (dimensionless).

    Use this for purely geometric / unitless math.
    If you need physical units (mm, m, ...), use Vector3D instead.
    """
    x: float
    y: float
    z: float

    def as_np(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z], dtype=float)

    def norm(self) -> float:
        return float(math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z))

    def normalized(self) -> Vec3:
        n = self.norm()
        if n == 0.0:
            raise ValueError("Cannot normalize zero vector.")
        return Vec3(self.x / n, self.y / n, self.z / n)

    def dot(self, other: Vec3) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: Vec3) -> Vec3:
        c = np.cross(self.as_np(), other.as_np())
        return Vec3(float(c[0]), float(c[1]), float(c[2]))

    def __add__(self, other: Vec3) -> Vec3:
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Vec3) -> Vec3:
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self) -> Vec3:
        return Vec3(-self.x, -self.y, -self.z)

    def __mul__(self, k: Number) -> Vec3:
        kk = float(k)
        return Vec3(self.x * kk, self.y * kk, self.z * kk)

    def __rmul__(self, k: Number) -> Vec3:
        return self.__mul__(k)

    def __truediv__(self, k: Number) -> Vec3:
        kk = float(k)
        if kk == 0.0:
            raise ZeroDivisionError("Division by zero.")
        return Vec3(self.x / kk, self.y / kk, self.z / kk)

    def __str__(self) -> str:
        return f"Vec3({self.x:.6g}, {self.y:.6g}, {self.z:.6g})"
