import numpy as np
import math
from dataclasses import dataclass
from allytools.units.length import Angle, AngleUnit
from gosti.basic.vec_2d import Vec2

@dataclass(frozen=True, slots=True)
class AngleVec2:
    theta_x: Angle
    theta_y: Angle

    def to_rad_np(self) -> np.ndarray:
        return np.array(
            [self.theta_x.to(AngleUnit.RAD), self.theta_y.to(AngleUnit.RAD)],
            dtype=float)

    def magnitude(self) -> Angle:
        # sqrt(theta_x^2 + theta_y^2) in radians -> Angle
        tx = self.theta_x.to(AngleUnit.RAD)
        ty = self.theta_y.to(AngleUnit.RAD)
        return Angle(math.hypot(tx, ty))

    def is_zero(self) -> bool:
        v = self.to_rad_np()
        return float(np.linalg.norm(v)) == 0.0

    def unit_direction(self) -> Vec2:
        """
        Returns a *dimensionless* unit vector in the direction of (theta_x, theta_y).
        This is exactly what your code uses for u_t.
        """
        v = self.to_rad_np()
        n = float(np.linalg.norm(v))
        if n == 0.0:
            raise ValueError("Cannot normalize zero angular vector.")
        return Vec2((float(v[0] / n)), float(v[1] / n))