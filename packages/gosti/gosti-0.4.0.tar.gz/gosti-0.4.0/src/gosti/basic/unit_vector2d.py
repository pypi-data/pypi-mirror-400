from __future__ import annotations
import numpy as np
import math
from dataclasses import dataclass
from typing import TYPE_CHECKING
from allytools.units import Angle, Length
from gosti.basic.aid import hypot2


if TYPE_CHECKING:
    from gosti.basic.vector_2d import Vector2D
    from gosti.basic.vec_2d import Vec2

@dataclass(frozen=True, slots=True)
class UnitVector2D:
    """2D unit vector (‖u‖ = 1)."""
    l: float
    m: float

    def __post_init__(self) -> None:
        n = hypot2(self.l, self.m)
        if not math.isclose(n, 1.0, rel_tol=1e-12, abs_tol=1e-12):
            raise ValueError(f"UnitVector2D must have unit norm, got {n}")

    def as_array(self) -> np.ndarray:
        return np.array([self.l, self.m], dtype=float)

    def dot(self, other: UnitVector2D) -> float:
        return self.l * other.l + self.m * other.m

    def perp(self) -> UnitVector2D:
        """Rotate by +90° (counter-clockwise)."""
        return UnitVector2D(-self.m, self.l)

    def angle(self) -> Angle:
        """Return polar angle."""
        return Angle(math.atan2(self.m, self.l))

    def to_vector(self, length: Length) -> Vector2D:
        """Convert direction to a Vector2D with given magnitude."""
        from gosti.basic.vector_2d import Vector2D
        mm = float(length.value_mm)
        return Vector2D(Length(mm * self.l), Length(mm * self.m))

    @staticmethod
    def from_angle(theta: Angle) -> UnitVector2D:
        t = float(theta.value_rad)
        return UnitVector2D(math.cos(t), math.sin(t))

    @staticmethod
    def from_vec2(v: Vec2) -> UnitVector2D:
        n = v.norm()
        if n == 0.0:
            raise ValueError("Cannot build UnitVector2D from zero Vec2.")
        return UnitVector2D(v.x / n, v.y / n)

    @staticmethod
    def from_vector(v: Vector2D) -> UnitVector2D:
        x = float(v.x.value_mm)
        y = float(v.y.value_mm)
        n = hypot2(x, y)
        if n == 0.0:
            raise ValueError("Cannot build UnitVector2D from zero Vector2D.")
        return UnitVector2D(x / n, y / n)

    def __str__(self) -> str:
        ang = self.angle().value_rad
        return f"UnitVector2D(l={self.l:.6f}, m={self.m:.6f}, θ={ang:.6e} rad)"