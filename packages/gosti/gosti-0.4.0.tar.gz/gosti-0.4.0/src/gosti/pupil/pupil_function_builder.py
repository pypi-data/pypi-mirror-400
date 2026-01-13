from __future__ import annotations
import numpy as np
from typing import Optional, TYPE_CHECKING
from gosti.wavelength import Wavelength
from gosti.pupil.pupil_grid import PupilGrid
from gosti.pupil.apodization import Apodization
from gosti.pupil.pupil_function import PupilFunction

if TYPE_CHECKING:
    from gosti.wavefront.wavefront import Wavefront


class PupilFunctionBuilder:
    @staticmethod
    def _shape_from_grid(grid: PupilGrid) -> tuple[int, int]:
        n = grid.grid_size
        return n, n

    @staticmethod
    def _as_f64(arr: np.ndarray | None, *, shape: tuple[int, int], name: str) -> np.ndarray:
        if arr is None:
            return np.zeros(shape, dtype=np.float64)
        out = np.asarray(arr, dtype=np.float64)
        if out.shape != shape:
            raise ValueError(f"{name} must have shape {shape}, got {out.shape}")
        return out

    @classmethod
    def from_grid(
        cls,
        *,
        grid: PupilGrid,
        wavelength: Wavelength,
        amplitude: Optional[np.ndarray] = None,
        apodization: Optional[Apodization] = None,
        phase_waves: Optional[np.ndarray] = None,
    ) -> PupilFunction:
        if amplitude is not None and apodization is not None:
            raise ValueError("Provide either amplitude or apodization, not both.")

        shape = cls._shape_from_grid(grid)

        W = cls._as_f64(phase_waves, shape=shape, name="phase_waves")

        if amplitude is None:
            if apodization is None:
                A = np.ones(shape, dtype=np.float64)
            else:
                A = np.asarray(apodization.amplitude(grid), dtype=np.float64)
        else:
            A = np.asarray(amplitude, dtype=np.float64)

        if A.shape != shape:
            raise ValueError(f"amplitude must have shape {shape}, got {A.shape}")

        return PupilFunction(
            grid=grid,
            wavelength=wavelength,
            amplitude=A,
            phase_waves=W,
        )

    @classmethod
    def from_wavefront(
        cls,
        *,
        wf: Wavefront,
        remove_piston: bool = False,
    ) -> PupilFunction:
        W = np.asarray(wf.phase_waves, dtype=np.float64)

        if remove_piston:
            m = wf.pupil_mask > 0
            if np.any(m):
                W = W.copy()
                W[m] -= float(W[m].mean())

        return cls.from_grid(grid=wf.grid, wavelength=wf.wavelength, amplitude=wf.amplitude, phase_waves=W)
