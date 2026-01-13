from __future__ import annotations
import numpy as np
from allytools.logger import get_logger
from gosti.pupil.pupil_function import PupilFunction
from gosti.psf.psf import PSF

log = get_logger(__name__)
class PsfBuilder:
    @staticmethod
    def _pad_center(arr: np.ndarray, pad_factor: int) -> np.ndarray:
        if pad_factor == 1:
            return arr
        h0, w0 = arr.shape
        h, w = pad_factor * h0, pad_factor * w0
        ph = (h - h0) // 2
        pw = (w - w0) // 2
        return np.pad(arr, ((ph, h - h0 - ph), (pw, w - w0 - pw)), constant_values=0.0)

    @staticmethod
    def _fft_pupil(pupil: np.ndarray) -> np.ndarray:
        return np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(pupil)))

    @classmethod
    def from_pupil_function(
        cls,
        pupil_function: PupilFunction,
        *,
        pad_factor: int = 1) -> PSF:
        if pad_factor < 1:
            raise ValueError(f"pad_factor must be >= 1, got {pad_factor}")
        pupil = pupil_function.complex_field()
        pupil = cls._pad_center(pupil, pad_factor)
        field = cls._fft_pupil(pupil)
        raw_intensity = (field * field.conj()).real
        return PSF(raw_intensity=raw_intensity, pad_factor=pad_factor)
