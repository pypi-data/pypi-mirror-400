from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import Optional
from gosti.basic.unit_vector3d import UnitVector3D
from gosti.pupil.pupil_mask_elliptical import PupilMaskElliptical

@dataclass(slots=True)
class PupilGrid:
    grid_size: int
    chief_direction: Optional[UnitVector3D] = None
    x_norm: np.ndarray = field(init=False, repr=False)
    y_norm: np.ndarray = field(init=False, repr=False)
    rho: np.ndarray = field(init=False, repr=False)
    phi: np.ndarray = field(init=False, repr=False)
    mask: np.ndarray = field(init=False, repr=False)
    def __post_init__(self) -> None:
        if self.grid_size <= 1:
            raise ValueError(f"grid_size must be > 1, got {self.grid_size}")
        lin = np.linspace(-1.0, 1.0, self.grid_size)
        x, y = np.meshgrid(lin, lin)
        x = -x
        y = -y
        self.x_norm = x
        self.y_norm = y
        self.rho = np.sqrt(x * x + y * y)
        self.phi = np.arctan2(y, x)
        if self.chief_direction is None:
            theta_x = theta_y = 0.0
        else:
            theta_x, theta_y = self.chief_direction.tilts()
        pmask = PupilMaskElliptical(theta_x=theta_x, theta_y=theta_y)
        self.mask = pmask.evaluate(self.x_norm, self.y_norm)


    @property
    def n_active(self) -> int:
        return int(self.mask.sum())

    @property
    def n_total(self) -> int:
        return int(self.grid_size * self.grid_size)