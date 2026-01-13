from __future__ import annotations
import math
import numpy as np
from dataclasses import dataclass
from allytools.units import Angle
from allytools.logger import get_logger
from gosti.basic.vec_2d import Vec2
from gosti.basic.ortho_basis import OrthoBasis2
from gosti.basic.elliptical_radii import EllipseRadii

log = get_logger(__name__)
@dataclass(frozen=True, slots=True)
class PupilMaskElliptical:
    theta_x: Angle
    theta_y: Angle
    min_cos: float = 1e-6

    def _radii(self) -> EllipseRadii:
        tx = float(self.theta_x.value_rad)
        ty = float(self.theta_y.value_rad)
        theta_mag = math.hypot(tx, ty)
        cos_raw = math.cos(theta_mag)
        cos_theta = max(cos_raw, self.min_cos)
        if cos_theta != cos_raw:
            log.debug("cos(theta) clamped: raw=%.3e → used=%.3e (|theta|=%.3e rad)",
                cos_raw, cos_theta, theta_mag)
        # tangential stretched, sagittal unchanged
        return EllipseRadii(r_tan=1.0 / cos_theta,r_sag=1.0)

    def evaluate(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        rhos = np.sqrt(x * x + y * y)
        # No tilt → circular pupil
        tx = float(self.theta_x.value_rad)
        ty = float(self.theta_y.value_rad)
        theta_mag = math.hypot(tx, ty)
        log.debug("Building pupil mask: theta_x=%.6e rad, theta_y=%.6e rad (|theta|=%.6e)",
                  tx, ty, theta_mag)
        if theta_mag < 1e-12:
            log.debug("Zero tilt → using circular pupil.")
            return rhos <= 1.0
        # Tangential direction from chief-ray tilt
        v_t = Vec2(tx, ty)
        try:
            basis = OrthoBasis2.from_tangential(v_t)
        except ValueError as e:
            log.debug("Failed to build tangential basis (%s) → using circular pupil.",e)
            return rhos <= 1.0
        # Project grid onto tangential / sagittal axes
        log.trace("Tangential basis: u_t=%s, u_s=%s",basis.u_t, basis.u_s)
        t, s = basis.project(x, y)
        R = self._radii()
        # Ellipse equation
        ellipse = (t / R.r_tan) ** 2 + (s / R.r_sag) ** 2
        return ellipse <= 1.0

