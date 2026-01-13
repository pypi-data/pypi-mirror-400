import numpy as np
from dataclasses import dataclass
from typing import Tuple

from allytools.logger import get_logger
from allytools.units import Angle, AngleUnit

log = get_logger(__name__)


@dataclass
class AngularGrid:
    """
    Angular grid (phi, theta) for surface parameterization.

    phi   ∈ [0, 2π)
    theta ∈ [0, theta_max]

    Internally stored in radians for NumPy compatibility.
    """
    n_phi: int
    n_theta: int
    theta_max: Angle  # ← now strongly typed

    def __post_init__(self):
        if not isinstance(self.theta_max, Angle):
            raise TypeError("theta_max must be an Angle")

        if self.theta_max.is_infinite():
            raise ValueError("theta_max cannot be infinite")

        theta_max_rad = self.theta_max.value_rad

        log.debug(
            "AngularGrid init: n_phi=%d n_theta=%d theta_max=%.6f rad (%.3f %s)",
            self.n_phi,
            self.n_theta,
            theta_max_rad,
            self.theta_max.value,
            self.theta_max.unit.symbol)

        # φ ∈ [0, 2π)
        self.phi = np.linspace(
            0.0,
            2.0 * np.pi,
            self.n_phi,
            endpoint=False,
            dtype=float)

        # θ ∈ [0, theta_max]
        self.theta = np.linspace(
            0.0,
            theta_max_rad,
            self.n_theta,
            dtype=float)

        self.PHI, self.THETA = np.meshgrid(self.phi, self.theta, indexing="xy")

        log.info(
            "AngularGrid created successfully (%d×%d points).",
            self.n_theta,
            self.n_phi)

    @property
    def shape(self) -> Tuple[int, int]:
        """Grid shape as (n_theta, n_phi)."""
        return self.n_theta, self.n_phi

    @property
    def theta_max_rad(self) -> float:
        """theta_max in radians."""
        return self.theta_max.value_rad

    @property
    def theta_max_deg(self) -> float:
        """theta_max in degrees."""
        return self.theta_max.to(AngleUnit.DEG)

    @property
    def theta_max_angle(self) -> Angle:
        """theta_max as Angle (preserves preferred unit)."""
        return self.theta_max


