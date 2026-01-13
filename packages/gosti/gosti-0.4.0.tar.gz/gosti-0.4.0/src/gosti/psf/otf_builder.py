from __future__ import annotations
import numpy as np
from allytools.units import Length
from gosti.psf.psf import PSF
from gosti.psf.otf import OTF


def _fft2c(x: np.ndarray) -> np.ndarray:
    return np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(x)))

class OtfBuilder:
    @staticmethod
    def from_psf(
        psf: PSF,
        *,
        wavelength: Length,
        exit_pupil_diameter: Length,
        exit_pupil_position: Length,
    ) -> OTF:
        # reuse your PSF sampling logic (dx derived from wavelength, pupil diameter, pad_factor, etc.)
        sf = psf.as_scalar_field(
            wavelength=wavelength,
            exit_pupil_diameter=exit_pupil_diameter,
            exit_pupil_position=exit_pupil_position)
        I = sf.values  # normalized intensity already in PSF.as_scalar_field()
        H = _fft2c(I)

        # normalize by DC (center after fftshift)
        cy, cx = (H.shape[0] // 2, H.shape[1] // 2)
        dc = H[cy, cx]
        if dc != 0:
            H = H / dc

        return OTF(values=H, dx=sf.dx, dy=sf.dy)
