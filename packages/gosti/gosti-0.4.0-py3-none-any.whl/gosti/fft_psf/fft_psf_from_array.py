import numpy as np
from allytools.logger import get_logger
from allytools.units import Length
from gosti.fft_psf.fft_psf import FftPsf
from gosti.scalar2d.scalar_field2d import ScalarField2D
from numpy.typing import NDArray

log = get_logger(__name__)
def fft_psf_from_array(
        *,
        values: NDArray[np.float64],
        field_x: Length,
        field_y: Length,
        wavelength: Length,
        dx: Length,
        dy: Length,
        min_x: Length,
        min_y: Length) -> FftPsf:

    scalar2d = ScalarField2D(
        values=values,
        min_x=min_x,
        min_y=min_y,
        dx=dx,
        dy=dy)

    log.debug(" ScalarField2D created: shape=%s",scalar2d.shape)
    fft_psf = FftPsf(
        scalar2d=scalar2d,
        wavelength= wavelength,
        field_x=field_x,
        field_y=field_y)
    log.info(" FftPsf created from Zemax FFT report: shape=%s",fft_psf.scalar2d.shape,)
    return fft_psf
