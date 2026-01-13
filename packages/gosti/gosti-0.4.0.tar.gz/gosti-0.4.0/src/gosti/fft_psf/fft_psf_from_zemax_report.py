import numpy as np
from pathlib import Path
from allytools.logger import get_logger
from allytools.units import Length, average_length
from gosti.fft_psf.fft_psf import FftPsf
from gosti.fft_psf.parse_zemax import read_zemax_fft_psf
from gosti.scalar2d.scalar_field2d import ScalarField2D

log = get_logger(__name__)

def fft_psf_from_zemax_report(*, path: Path) -> FftPsf:
    psf, x_mm, y_mm, meta = read_zemax_fft_psf(path)

    if psf.ndim != 2:
        raise ValueError(f"Zemax FFT PSF must be 2D, got shape={psf.shape}")

    ny, nx = psf.shape

    # --- spacing (prefer meta if you have it; otherwise infer from x_mm/y_mm)
    if getattr(meta, "dx_mm", None) is not None:
        dx_mm = float(meta.dx_mm)
    else:
        dx_mm = float(np.diff(x_mm).mean()) if nx > 1 else 0.0

    if getattr(meta, "dy_mm", None) is not None:
        dy_mm = float(meta.dy_mm)
    else:
        dy_mm = float(np.diff(y_mm).mean()) if ny > 1 else 0.0

    dx_mm = abs(dx_mm)
    dy_mm = abs(dy_mm)

    # --- Zemax center point (1-based)
    r0 = int(meta.center_row)   # e.g. 129
    c0 = int(meta.center_col)   # e.g. 128

    # --- Zemax prints top->bottom, so flip to make y increase upward (optional but common)
    psf = psf[::-1, :].copy()

    # after flip, the center row index changes:
    r0 = ny + 1 - r0

    # --- build axes from center point (pixel centers!)
    # 0-based i,j -> 1-based (i+1),(j+1)
    x0_mm = (1 - c0) * dx_mm
    y0_mm = (1 - r0) * dy_mm

    scalar2d = ScalarField2D(
        values=psf,
        min_x=Length(x0_mm),
        min_y=Length(y0_mm),
        dx=Length(dx_mm),
        dy=Length(dy_mm),
    )

    log.debug("ScalarField2D: shape=%s, min=(%.6g, %.6g) mm, d=(%.6g, %.6g) mm",
              psf.shape, x0_mm, y0_mm, dx_mm, dy_mm)

    return FftPsf(
        scalar2d=scalar2d,
        wavelength=average_length(meta.wavelength_min, meta.wavelength_max),
        field_x=meta.field_x,
        field_y=meta.field_y,
    )
