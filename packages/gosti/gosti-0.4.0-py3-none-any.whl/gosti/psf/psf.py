from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from allytools.logger import get_logger
from allytools.units import Length, LengthUnit, Angle, AngleUnit
from gosti.scalar2d.scalar_field2d import ScalarField2D

log = get_logger(__name__)
@dataclass(frozen=True, slots=True)
class PSF:
    raw_intensity: np.ndarray
    pad_factor: int

    @property
    def normalized_intensity(self) -> np.ndarray:
        I = self.raw_intensity
        s = float(I.sum())
        if s > 0.0:
            return I / s
        return I

    @property
    def energy(self) -> float:
        return float(self.raw_intensity.sum())

    @property
    def peak(self) -> float:
        return float(self.raw_intensity.max())


    def as_scalar_field(
            self,
            *,
            wavelength: Length,
            exit_pupil_diameter: Length,
            exit_pupil_position: Length) -> ScalarField2D:
        h, w = self.raw_intensity.shape

        delta_theta = Angle(wavelength / (exit_pupil_diameter * self.pad_factor))
        delta_x = exit_pupil_position * delta_theta.value_rad  # same for x/y
        log.debug("Δθ = %.3e [rad], Δx = %.3f [um]",
            delta_theta.to(AngleUnit.RAD),
                  delta_x.to(LengthUnit.UM))
        x_idx = np.arange(w) - w // 2
        y_idx = np.arange(h) - h // 2
        dx = delta_x
        dy = delta_x
        min_x = x_idx[0] * dx
        min_y = y_idx[0] * dy

        log.debug("Image-plane sampling: dx=%.3e [um], grid=%dx%d, min_x=%.1e [um], min_y=%.1e [um]",
            dx.to(LengthUnit.UM),
            h,
            w,
            min_x.to(LengthUnit.UM),
            min_y.to(LengthUnit.UM))

        return ScalarField2D(
            values=self.normalized_intensity.astype(np.float64, copy=False),
            min_x=min_x,
            min_y=min_y,
            dx=dx,
            dy=dy)