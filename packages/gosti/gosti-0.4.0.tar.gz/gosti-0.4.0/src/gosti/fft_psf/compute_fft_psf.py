import numpy as np
from typing import Optional
from allytools.logger import get_logger
from allytools.units import Length
from gosti.pupil.pupil_grid import build_pupil_grid
from gosti.zernike.zernike_base import ZernikeBasis
from gosti.scalar2d.scalar_field2d import ScalarField2D
from gosti.basic.unit_vector3d import UnitVector3D
from gosti.pupil.pupil_function_builder import PupilFunctionBuilder
from gosti.pupil.apodizations import UniformApodization
from gosti.psf.psf_builder import PsfBuilder
from gosti.pupil.vis import visualize_pupil_grid_mesh
from gosti.wavefront.wavefront_builder import WFBuilder
from gosti.wavelength import Wavelength

log = get_logger(__name__)
def compute_fft_psf(
    *,
    coefficients: np.ndarray,
    wavelength: Wavelength,
    exit_pupil_diameter: Length,
    exit_pupil_position: Length,
    grid_size: int,
    pad_factor: int = 4,
    field_x_img: Optional[Length] = None,
    field_y_img: Optional[Length] = None) -> ScalarField2D:
    chief_direction = UnitVector3D.from_slopes(slope_x=field_x_img / exit_pupil_position,
                                               slope_y=field_y_img / exit_pupil_position)
    #grid = build_pupil_grid(grid_size=grid_size, chief_direction=chief_direction)
    grid = build_pupil_grid(grid_size=grid_size, chief_direction=None)
    n_coef = coefficients.shape[0]
    basis_flat = ZernikeBasis().build_basis(n_coef, grid)
    phase_waves = (coefficients[:n_coef] @ basis_flat).reshape(grid_size, grid_size)
    #visualize_pupil_grid_mesh(grid)
    pupil_function = PupilFunctionBuilder.from_grid(
        grid=grid,
        wavelength=wavelength,
        apodization=UniformApodization(),
        phase_waves=phase_waves)
    w_org = WFBuilder.from_pupil_function(pupil_function)
    w_org.visualize()
    psf = PsfBuilder.from_pupil_function(pupil_function=pupil_function, pad_factor=pad_factor)
    scalar2d = psf.as_scalar_field(wavelength=wavelength,
                                   exit_pupil_diameter=exit_pupil_diameter,
                                   exit_pupil_position=exit_pupil_position)

    return scalar2d
