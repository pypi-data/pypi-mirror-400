from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from allytools.units import Length
from gosti.basic.aid import hypot2
from gosti.basic.unit_vector2d import UnitVector2D
from gosti.basic.aid import Number

@dataclass(frozen=True, slots=True)
class Vector2D:
    """2D displacement vector with Length units."""
    x: Length
    y: Length

    def as_mm(self) -> np.ndarray:
        return np.array([float(self.x.value_mm), float(self.y.value_mm)], dtype=float)

    def norm(self) -> Length:
        x_mm = float(self.x.value_mm)
        y_mm = float(self.y.value_mm)
        return Length(hypot2(x_mm, y_mm))

    def normalized(self) -> UnitVector2D:
        n = float(self.norm().value_mm)
        if n == 0.0:
            raise ValueError("Cannot normalize zero Vector2D.")
        return UnitVector2D(float(self.x.value_mm) / n, float(self.y.value_mm) / n)

    def dot(self, other: Vector2D) -> float:
        """Dot product in mm^2 (returned as float)."""
        a = self.as_mm()
        b = other.as_mm()
        return float(a @ b)

    def cross_z(self, other: Vector2D) -> float:
        """2D cross product z-component in mm^2 (returned as float)."""
        ax, ay = self.as_mm()
        bx, by = other.as_mm()
        return float(ax * by - ay * bx)

    def __add__(self, other: Vector2D) -> Vector2D:
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2D) -> Vector2D:
        return Vector2D(self.x - other.x, self.y - other.y)

    def __neg__(self) -> Vector2D:
        return Vector2D(-self.x, -self.y)

    def __mul__(self, k: Number) -> Vector2D:
        kk = float(k)
        return Vector2D(Length(float(self.x.value_mm) * kk), Length(float(self.y.value_mm) * kk))

    def __rmul__(self, k: Number) -> Vector2D:
        return self.__mul__(k)

    def __truediv__(self, k: Number) -> Vector2D:
        kk = float(k)
        if kk == 0.0:
            raise ZeroDivisionError("Division by zero.")
        return Vector2D(Length(float(self.x.value_mm) / kk), Length(float(self.y.value_mm) / kk))

    def __str__(self) -> str:
        return f"Vector2D(x={self.x}, y={self.y})"
