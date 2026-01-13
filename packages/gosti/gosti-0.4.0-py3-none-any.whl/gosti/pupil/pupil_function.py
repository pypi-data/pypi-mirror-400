from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from allytools.units import LengthUnit, LengthArray
from gosti.pupil.pupil_grid import PupilGrid
from gosti.wavelength import Wavelength

@dataclass(frozen=True, slots=True)
class PupilFunction:
    grid: PupilGrid
    wavelength: Wavelength
    amplitude: np.ndarray        # shape (N, N)
    phase_waves: np.ndarray      # shape (N, N), in waves

    @property
    def mask(self) -> np.ndarray:
        return self.grid.mask

    @property
    def boolean_mask(self) -> np.ndarray:
        return self.mask > 0

    @property
    def has_pupil(self) -> bool:
        return bool(np.any(self.boolean_mask))

    @property
    def n_active(self) -> int:
        return int(np.count_nonzero(self.mask))

    @property
    def weights(self) -> np.ndarray:
        m = (self.mask > 0).astype(np.float64)
        I = self.amplitude.astype(np.float64) ** 2
        return m * I

    @property
    def opd(self) -> LengthArray:
        lam_um = self.wavelength.to(LengthUnit.UM)
        opd_um = self.phase_waves * lam_um
        opd_um = np.where(self.mask > 0, opd_um, 0.0)
        return LengthArray.from_value(opd_um, LengthUnit.UM)

    def _complex_from_phase(self, w: np.ndarray) -> np.ndarray:
        return (self.mask * self.amplitude) * np.exp(1j * (2.0 * np.pi) * w)

    def complex_field(self) -> np.ndarray:
        return self._complex_from_phase(self.phase_waves)

    def complex_field_no_piston(self) -> np.ndarray:
        pw = self.phase_waves
        m = self.mask > 0
        if np.any(m):
            pw = pw.copy()
            pw[m] -= float(pw[m].mean())
        return self._complex_from_phase(pw)