from __future__ import annotations
import numpy as np
import math
from typing import TYPE_CHECKING
from dataclasses import dataclass
from gosti.basic.aid import hypot3
from allytools.units import Angle, Length, AngleUnit

if TYPE_CHECKING:
    from gosti.basic.vector_3d import Vector3D
    from gosti.basic.vec_3d import Vec3

@dataclass(frozen=True, slots=True)
class UnitVector3D:
    """3D unit vector (‖u‖ = 1).l, m, n - direction cosines"""
    l: float
    m: float
    n: float


    def __post_init__(self) -> None:
        n = hypot3(self.l, self.m, self.n)
        if not math.isclose(n, 1.0, rel_tol=1e-12, abs_tol=1e-12):
            raise ValueError(f"UnitVector3D must have unit norm, got {n}")

    def as_array(self) -> np.ndarray:
        return np.array([self.l, self.m, self.n], dtype=float)

    def dot(self, other: UnitVector3D) -> float:
        return self.l * other.l + self.m * other.m + self.n * other.n

    def cross(self, other: UnitVector3D) -> UnitVector3D:
        c = np.cross(self.as_array(), other.as_array())
        n = hypot3(*c)
        if n == 0.0:
            raise ValueError("Cross product is zero; vectors are parallel.")
        return UnitVector3D(c[0] / n, c[1] / n, c[2] / n)

    def slopes(self) -> tuple[float, float]:
        if self.n == 0.0:
            raise ValueError("Cannot compute slopes when n == 0.")
        return self.l / self.n, self.m / self.n

    def tilts_rad(self) -> tuple[float, float]:
        """Tilt angles in radians as floats: (theta_x, theta_y)."""
        sx, sy = self.slopes()
        return math.atan(sx), math.atan(sy)

    def tilts(self) -> tuple[Angle, Angle]:
        """Tilt angles as Angle objects."""
        tx, ty = self.tilts_rad()
        return Angle(tx), Angle(ty)

    def to_vector(self, length: Length) -> Vector3D:
        """Convert direction to a Vector3D with given magnitude."""
        from gosti.basic.vector_3d import Vector3D
        mm = float(length.value_mm)
        return Vector3D(Length(mm * self.l), Length(mm * self.m), Length(mm * self.n))

    @staticmethod
    def from_slopes(*, slope_x: float, slope_y: float, require_forward: bool = True) -> UnitVector3D:
        nn = hypot3(slope_x, slope_y, 1.0)
        u = UnitVector3D(slope_x / nn, slope_y / nn, 1.0 / nn)
        if require_forward and u.n <= 0.0:
            raise ValueError("Expected forward direction (+z).")
        return u

    @staticmethod
    def from_vector(v: "Vector3D", *, require_forward: bool = False) -> UnitVector3D:
        x = float(v.x.value_mm)
        y = float(v.y.value_mm)
        z = float(v.z.value_mm)
        nn = hypot3(x, y, z)
        if nn == 0.0:
            raise ValueError("Cannot build UnitVector3D from zero Vector3D.")
        u = UnitVector3D(x / nn, y / nn, z / nn)
        if require_forward and u.n <= 0.0:
            raise ValueError("Expected forward direction (+z), got n <= 0.")
        return u

    @staticmethod
    def from_vec3(v: "Vec3", *, require_forward: bool = False) -> UnitVector3D:
        nn = v.norm()
        if nn == 0.0:
            raise ValueError("Cannot build UnitVector3D from zero Vec3.")
        u = UnitVector3D(v.x / nn, v.y / nn, v.z / nn)
        if require_forward and u.n <= 0.0:
            raise ValueError("Expected forward direction (+z).")
        return u

    @staticmethod
    def from_thetas(theta_x: Angle, theta_y: Angle, paraxial: bool = False) -> UnitVector3D:
        tx = float(theta_x.value_rad)
        ty = float(theta_y.value_rad)
        sx = tx if paraxial else math.tan(tx)
        sy = ty if paraxial else math.tan(ty)
        return UnitVector3D.from_slopes(sx, sy)

    def __str__(self) -> str:
        sx, sy = self.slopes()
        return (
            f"UnitVector3D(l={self.l:.6f}, m={self.m:.6f}, n={self.n:.6f}, "
            f"sx={sx:.3e}, sy={sy:.3e})"
        )
