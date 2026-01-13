from dataclasses import dataclass
import numpy as np
from gosti.zernike.zernike_base import ZernikeBasis

@dataclass(frozen=True)
class ZernikeProjection:
    coefficients: np.ndarray
    basis: ZernikeBasis
    n_coef: int
    rms_residual: float
