from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from typing import Optional
from allytools.units import  Angle
from gosti.basic.unit_vector3d import UnitVector3D
from gosti.pupil.pupil_mask_elliptical import PupilMaskElliptical

@dataclass(frozen=True, slots=True)
class PupilGrid:
    grid_size: int
    chief_direction: Optional[UnitVector3D]
    x_norm: np.ndarray
    y_norm: np.ndarray
    rho: np.ndarray
    phi: np.ndarray
    mask: np.ndarray

    @property
    def n_total(self) -> int:
        gs = self.grid_size
        return int(gs * gs)

    @property
    def n_active(self) -> int:
        return int(np.count_nonzero(self.mask))

def build_pupil_grid(*, grid_size:int, chief_direction: Optional[UnitVector3D]) -> PupilGrid:
    if grid_size <= 1:
        raise ValueError(f"grid_size must be > 1, got {grid_size}")
    lin = np.linspace(-1.0, 1.0, grid_size, dtype=np.float64)
    x, y = np.meshgrid(lin, lin)
    x = -x
    y = -y
    rho = np.sqrt(x * x + y * y)
    phi = np.arctan2(y, x)
    if chief_direction is None:
        theta_x = theta_y = Angle.zero_angle()
    else:
        theta_x, theta_y = chief_direction.tilts()
    pmask = PupilMaskElliptical(theta_x=theta_x, theta_y=theta_y)
    mask = pmask.evaluate(x, y)
    return PupilGrid(grid_size=grid_size,chief_direction=chief_direction,x_norm=x,y_norm=y,rho=rho,phi=phi,mask=mask)
