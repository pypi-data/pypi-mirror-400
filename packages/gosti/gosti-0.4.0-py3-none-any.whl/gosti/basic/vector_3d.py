from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from allytools.units import Length
from gosti.basic.aid import hypot3
from gosti.basic.unit_vector3d import UnitVector3D
from gosti.basic.aid import Number

@dataclass(frozen=True, slots=True)
class Vector3D:
    """3D displacement vector with Length units."""
    x: Length
    y: Length
    z: Length

    def as_mm(self) -> np.ndarray:
        return np.array(
            [float(self.x.value_mm), float(self.y.value_mm), float(self.z.value_mm)],
            dtype=float,
        )

    def norm(self) -> Length:
        x_mm = float(self.x.value_mm)
        y_mm = float(self.y.value_mm)
        z_mm = float(self.z.value_mm)
        return Length(hypot3(x_mm, y_mm, z_mm))

    def normalized(self) -> UnitVector3D:
        n = float(self.norm().value_mm)
        if n == 0.0:
            raise ValueError("Cannot normalize zero Vector3D.")
        return UnitVector3D(float(self.x.value_mm) / n, float(self.y.value_mm) / n, float(self.z.value_mm) / n)

    def dot(self, other: Vector3D) -> float:
        """Dot product in mm^2 (returned as float)."""
        a = self.as_mm()
        b = other.as_mm()
        return float(a @ b)

    def cross(self, other: Vector3D) -> Vector3D:
        """Cross product in mm^2 along each axis (returned as Vector3D of Length)."""
        c = np.cross(self.as_mm(), other.as_mm())
        return Vector3D(Length(float(c[0])), Length(float(c[1])), Length(float(c[2])))

    def __add__(self, other: Vector3D) -> Vector3D:
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Vector3D) -> Vector3D:
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self) -> Vector3D:
        return Vector3D(-self.x, -self.y, -self.z)

    def __mul__(self, k: Number) -> Vector3D:
        kk = float(k)
        return Vector3D(
            Length(float(self.x.value_mm) * kk),
            Length(float(self.y.value_mm) * kk),
            Length(float(self.z.value_mm) * kk),
        )

    def __rmul__(self, k: Number) -> Vector3D:
        return self.__mul__(k)

    def __truediv__(self, k: Number) -> Vector3D:
        kk = float(k)
        if kk == 0.0:
            raise ZeroDivisionError("Division by zero.")
        return Vector3D(
            Length(float(self.x.value_mm) / kk),
            Length(float(self.y.value_mm) / kk),
            Length(float(self.z.value_mm) / kk))

    def __str__(self) -> str:
        return f"Vector3D(x={self.x}, y={self.y}, z={self.z})"
