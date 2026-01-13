from dataclasses import dataclass
from typing import Protocol
import numpy as np

from allytools.logger import get_logger
from gosti.grids.angular_grid import AngularGrid

log = get_logger(__name__)


class DeformationBasis(Protocol):
    """A typed basis that can be evaluated on an AngularGrid."""
    def n_coeffs(self) -> int: ...
    def evaluate(self, grid: AngularGrid) -> np.ndarray:
        """
        Returns basis array B with shape (K, n_theta, n_phi) as floats (dimensionless).
        """


@dataclass(frozen=True)
class FourierPhiBasis:
    """
    Simple example basis:
      B_k(θ,φ) = cos(m_k * φ) * sin(θ)
    Good as a placeholder; replace with your real basis (Zernike, etc.).
    """
    m: tuple[int, ...]  # modes along phi

    def n_coeffs(self) -> int:
        return len(self.m)

    def evaluate(self, grid: AngularGrid) -> np.ndarray:
        PHI = grid.PHI
        THETA = grid.THETA
        out = np.empty((len(self.m), grid.n_theta, grid.n_phi), dtype=float)
        s = np.sin(THETA)
        for k, mk in enumerate(self.m):
            out[k] = np.cos(mk * PHI) * s
        return out