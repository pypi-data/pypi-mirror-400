from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from allytools.units import Angle
from gosti.pupil.pupil_grid import PupilGrid
from gosti.pupil.apodization import ApodizationType, Apodization

@dataclass(frozen=True, slots=True)
class UniformApodization(Apodization):
    kind: ApodizationType = ApodizationType.UNIFORM

    def amplitude(self, grid: PupilGrid) -> np.ndarray:
        N = grid.grid_size
        return np.ones((N, N), dtype=np.float64)


@dataclass(frozen=True, slots=True)
class GaussianApodization(Apodization):
    """
    Zemax-like Gaussian amplitude:
        A(ρ) = exp( - G * ρ^2 )
    - A(0)=1
    - G=1 => A(1)=exp(-1)=1/e at pupil edge
    """
    G: float
    kind: ApodizationType = ApodizationType.GAUSSIAN

    def __post_init__(self) -> None:
        if self.G < 0.0:
            raise ValueError("Gaussian apodization factor G must be >= 0.")

    def amplitude(self, grid: PupilGrid) -> np.ndarray:
        return np.exp(-float(self.G) * grid.rho * grid.rho)

@dataclass(frozen=True, slots=True)
class CosineCubedApodization(Apodization):
    """
    Zemax 'cosine cubed' intensity falloff.

    Intensity:
        I ∝ cos^3(theta)

    Amplitude:
        A = sqrt(I) = cos(theta)^(3/2)

    Mapping to pupil coordinate:
        tan(theta) = rho * tan(theta_marginal)

    Therefore:
        A(rho) = (1 + (rho * tan(theta_marginal))^2)^(-3/4)

    Notes
    -----
    - theta_marginal is the angle between optical axis and marginal ray
    - Must be provided as a physical Angle (not a raw float)
    """
    theta_marginal: Angle
    kind: ApodizationType = ApodizationType.COSINE_CUBED

    def __post_init__(self) -> None:
        if self.theta_marginal < Angle(0.0):
            raise ValueError("theta_marginal must be >= 0.")

    def amplitude(self, grid: PupilGrid) -> np.ndarray:
        tan_theta_marginal = np.tan(self.theta_marginal.value_rad)
        A = (1.0 + (grid.rho * tan_theta_marginal) ** 2) ** (-0.75)
        return A