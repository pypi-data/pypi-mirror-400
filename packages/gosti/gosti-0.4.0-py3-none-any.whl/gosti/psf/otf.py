from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from allytools.logger import get_logger
from allytools.units import Length

log = get_logger(__name__)
@dataclass(frozen=True, slots=True)
class OTF:
    values: np.ndarray        # complex (N,N), centered, OTF(0)=1
    dx: Length                   # image-plane sampling
    dy: Length

    @property
    def mtf(self) -> np.ndarray:
        return np.abs(self.values)

    @property
    def ptf(self) -> np.ndarray:
        return np.angle(self.values)

    def spatial_frequency_axes(self):
        fx = np.fft.fftshift(np.fft.fftfreq(self.values.shape[1], d=self.dx.value_mm))
        fy = np.fft.fftshift(np.fft.fftfreq(self.values.shape[0], d=self.dy.value_mm))
        return fx, fy