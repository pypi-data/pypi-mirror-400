from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from allytools.units import LengthArray
from imagera.pv_vis import pv_scalar_field_2d
from gosti.pupil.pupil_function import PupilFunction
from allytools.logger import get_logger

log = get_logger(__name__)
@dataclass(frozen=True, slots=True)
class Wavefront:
    pupil_function: PupilFunction

    def __post_init__(self) -> None:
        log.info ("rms mean - %.4f", self.rms_waves_weighted_mean_removed())
        log.info ("rms zemax - %.4f", self.rms_waves_zemax_like())
        log.info ("pv - %.4f", self.pv_waves())
        log.info ("pistone - %.4f", self.piston_waves())
        np.savetxt("py front.txt", self.phase_waves, fmt="% .6E")


    @property
    def phase_waves(self) -> np.ndarray:
        return np.asarray(self.pupil_function.opd / self.pupil_function.wavelength)

    @property
    def phase_rad(self) -> np.ndarray:
        return (2.0 * np.pi) * self.phase_waves

    def pv_waves(self, remove_piston: bool = True) -> float:
        Wv, wv, *_rest, sw = self._valid_vectors()
        log.info ("max - %.4f min - %.4f", Wv.max(),Wv.min())
        if sw <= 0 or Wv.size == 0:
            return 0.0
        if remove_piston:
            piston = float(np.sum(wv * Wv) / sw)
            Wv -= piston
        log.info ("max - %.4f min - %.4f", Wv.max(),Wv.min())
        log.info ("max - %.4f min - %.4f", self.phase_waves.max(),self.phase_waves.min())
        return float(Wv.max() - Wv.min())

    def piston_waves(self) -> float:
        Wv, wv, *_rest, sw = self._valid_vectors()
        if sw <= 0 or Wv.size == 0:
            return 0.0
        return float(np.sum(wv * Wv) / sw)

    def rms_waves_weighted_mean_removed(self) -> float:
        Wv, wv, *_rest, sw = self._valid_vectors()
        if sw <= 0 or Wv.size == 0:
            return 0.0
        mean = float(np.sum(wv * Wv) / sw)
        mean2 = float(np.sum(wv * Wv * Wv) / sw)
        var = mean2 - mean * mean
        return float(np.sqrt(max(var, 0.0)))

    def rms_waves_zemax_like(self) -> float:
        Wv, wv, xv, yv, rv2, sw = self._valid_vectors()
        if sw <= 0 or Wv.size == 0:
            return 0.0
        # Basis for reference sphere: piston + tip + tilt + defocus
        A = np.stack([np.ones_like(xv), xv, yv, rv2], axis=1)  # (N, 4)
        WA = A * wv[:, None]
        ATA = A.T @ WA
        ATb = A.T @ (wv * Wv)
        c = np.linalg.solve(ATA, ATb)
        R = Wv - (A @ c)
        mean = float(np.sum(wv * R) / sw)
        var = float(np.sum(wv * (R - mean) ** 2) / sw)
        return float(np.sqrt(max(var, 0.0)))

    def _valid_vectors(self) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
        """
        Returns masked vectors for wavefront computations.

        (Wv, wv, xv, yv, rv2, sw)
        """
        pf = self.pupil_function
        if not pf.has_pupil:
            z = np.asarray([], dtype=float)
            return z, z, z, z, z, 0.0

        m = pf.boolean_mask
        W = self.phase_waves.astype(float)                # (H, W)
        w = pf.weights.astype(float)                      # (H, W)
        x = pf.grid.x_norm.astype(float)                  # (H, W)
        y = pf.grid.y_norm.astype(float)                  # (H, W)

        Wv = W[m]
        wv = w[m]
        xv = x[m]
        yv = y[m]
        rv2 = xv * xv + yv * yv
        sw = float(np.sum(wv))
        return Wv, wv, xv, yv, rv2, sw

    def visualize(self):
        p = pv_scalar_field_2d(
            x=self.pupil_function.grid.x_norm,
            y=self.pupil_function.grid.y_norm,
            field=self.phase_waves,
            mask=self.pupil_function.boolean_mask, scalar_name="wavefront [waves]")
        p.show()

