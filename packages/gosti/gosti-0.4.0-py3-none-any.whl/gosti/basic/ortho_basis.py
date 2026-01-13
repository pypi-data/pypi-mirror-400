from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from gosti.basic.vec_2d import Vec2

@dataclass(frozen=True, slots=True)
class OrthoBasis2:
    """
    Orthonormal basis in 2D:
      u_t: tangential unit vector
      u_s: sagittal unit vector (perpendicular)
    """
    u_t: Vec2
    u_s: Vec2

    @staticmethod
    def from_tangential(v_t: Vec2) -> OrthoBasis2:
        u_t = v_t.normalized()
        u_s = u_t.perp_ccw()
        return OrthoBasis2(u_t=u_t, u_s=u_s)

    def project(self, x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Project points (x,y) into (t,s) coordinates.
        x,y are numpy arrays (same shape).
        """
        t = x * self.u_t.x + y * self.u_t.y
        s = x * self.u_s.x + y * self.u_s.y
        return t, s