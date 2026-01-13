from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, Sequence
from allytools.logger import get_logger
from allytools.units.length import Length
from allytools.vector import normalize
from gosti.grids.angular_grid import AngularGrid
from gosti.surface.basis import DeformationBasis



log = get_logger(__name__)
@dataclass
class FreeformSurfaceAngular:
    """
    Typed & fast freeform surface:

      r(θ,φ) = r0 + Σ c_k * B_k(θ,φ)

    - r0 is Length (internally mm)
    - c_k are floats (dimensionless) scaling the dimensionless basis
      (so the deformation has units of mm because it scales r0_mm? No.)
    IMPORTANT: If you want deformation in mm directly, interpret c_k as mm by
    multiplying basis by c_k_mm. See note below.

    Points returned in mm.
    """
    grid: AngularGrid
    r0: Length
    basis: DeformationBasis
    coeffs: np.ndarray  # shape (K,), float

    _B: Optional[np.ndarray] = field(default=None, init=False, repr=False)        # (K, n_theta, n_phi)
    _r_mm: Optional[np.ndarray] = field(default=None, init=False, repr=False)     # (n_theta, n_phi)
    _points: Optional[np.ndarray] = field(default=None, init=False, repr=False)
    _normals: Optional[np.ndarray] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.grid, AngularGrid):
            raise TypeError("grid must be an AngularGrid")
        if not isinstance(self.r0, Length):
            raise TypeError("r0 must be a Length")

        k = self.basis.n_coeffs()
        coeffs = np.asarray(self.coeffs, dtype=float)
        if coeffs.shape != (k,):
            raise ValueError(f"coeffs must have shape ({k},), got {coeffs.shape}")

        # store normalized coeffs array (float)
        self.coeffs = coeffs

        # precompute basis and r
        self._B = self.basis.evaluate(self.grid)
        if self._B.shape != (k, self.grid.n_theta, self.grid.n_phi):
            raise ValueError(
                f"basis.evaluate returned {self._B.shape}, expected {(k, self.grid.n_theta, self.grid.n_phi)}"
            )

        self._recompute_r_mm()

    def _recompute_r_mm(self) -> None:
        assert self._B is not None
        # r_mm = r0_mm + Σ c_k * B_k
        # Here coeffs are interpreted as mm (recommended).
        # If you want coeffs to be dimensionless, change to r0_mm*(1 + Σ c_k*B_k).
        r0_mm = float(self.r0.value_mm)
        self._r_mm = r0_mm + np.tensordot(self.coeffs, self._B, axes=(0, 0))
        self._points = None
        self._normals = None

    @property
    def r_mm(self) -> np.ndarray:
        assert self._r_mm is not None
        return self._r_mm

    def set_coeffs(self, coeffs: Sequence[float]) -> None:
        """Typed update of deformation coefficients (invalidates caches)."""
        coeffs_arr = np.asarray(coeffs, dtype=float)
        if coeffs_arr.shape != self.coeffs.shape:
            raise ValueError(f"coeffs must have shape {self.coeffs.shape}, got {coeffs_arr.shape}")
        self.coeffs = coeffs_arr
        self._recompute_r_mm()

    def points(self) -> np.ndarray:
        if self._points is not None:
            return self._points

        PHI = self.grid.PHI
        THETA = self.grid.THETA

        u = np.stack(
            [
                np.sin(THETA) * np.cos(PHI),
                np.sin(THETA) * np.sin(PHI),
                np.cos(THETA),
            ],
            axis=-1,
        )

        P = self.r_mm[..., None] * u
        self._points = P
        return P

    def normals(self) -> np.ndarray:
        if self._normals is not None:
            return self._normals

        P = self.points()

        dP_dtheta = np.zeros_like(P)
        dP_dphi = np.zeros_like(P)

        dP_dtheta[1:-1] = 0.5 * (P[2:] - P[:-2])
        dP_dtheta[0] = P[1] - P[0]
        dP_dtheta[-1] = P[-1] - P[-2]

        dP_dphi[:] = 0.5 * (np.roll(P, -1, axis=1) - np.roll(P, 1, axis=1))

        N = np.cross(dP_dtheta, dP_dphi, axis=-1)
        N = normalize(N)
        self._normals = N
        return N

    def invalidate(self) -> None:
        """Invalidate cached points/normals (r stays the same)."""
        self._points = None
        self._normals = None

    def default_scalar_name(self) -> str:
        # Most useful field for coloring in viewer
        return "r_mm"

    def scalar(self, name: str) -> np.ndarray:
        # Provide common scalar fields for visualization/debug
        if name == "r_mm":
            return self.r_mm
        if name == "z":
            return self.points()[..., 2]
        raise KeyError(f"Unknown scalar '{name}'. Available: 'r_mm', 'z'")

    def is_periodic_v(self) -> bool:
        # v-axis is phi -> periodic
        return True

