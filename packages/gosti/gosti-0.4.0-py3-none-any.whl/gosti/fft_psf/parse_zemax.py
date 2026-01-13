import logging
import re
import numpy as np
from typing import Tuple
from pathlib import Path
from allytools.units import LengthUnit, make_length
from allytools.files import require_file
from gosti.fft_psf.zemax_fft_psf_meta import FftPsfMeta

log = logging.getLogger(__name__)

def read_zemax_fft_psf(
    path: Path,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, FftPsfMeta]:
    """
    Parse Zemax text export: "Listing of FFT PSF Data".

    Expected header lines, for example:
        Polychromatic FFT PSF
        0.4500 to 0.4500 µm at 4.0000, 0.0000 mm.
        Data spacing is 0.400 µm.
        Data area is 102.400 µm wide.
        Image grid size: 256 by 256
        Center point is: row 129, column 128
        Values are not normalized.

    After the header, PSF values follow in row-major order.

    Returns
    -------
    psf : ndarray, shape (Ny, Nx)
        PSF intensity, exactly as in the file (no normalization).
    x_mm : ndarray, shape (Nx,)
        X coordinates in mm, with 0 at the PSF center (center column).
    y_mm : ndarray, shape (Ny,)
        Y coordinates in mm, with 0 at the PSF center (center row).
    meta : FftPsfMeta
        Parsed metadata with Length-typed quantities.
    """
    log.debug("Reading Zemax FFT PSF from %s", path)

    spacing_value: float | None = None
    spacing_token: str | None = None
    area_value: float | None = None
    area_token: str | None = None
    nx: int | None = None
    ny: int | None = None
    center_row: int | None = None
    center_col: int | None = None
    wavelength_min_val: float | None = None
    wavelength_max_val: float | None = None
    wl_unit_token: str | None = None
    field_x_val: float | None = None
    field_y_val: float | None = None
    field_unit_token: str | None = None
    data_values: list[float] = []
    in_data = False

    require_file(path=path, suffixes=(".txt", ".dat"))

    with path.open(encoding="utf-16") as f:
        for line in f:
            line_stripped = line.strip()
            if not in_data:
                m = re.search(
                    r"([0-9.+\-Ee]+)\s+to\s+([0-9.+\-Ee]+)\s*([^\s]+)\s+at\s+"
                    r"([0-9.+\-Ee]+),\s*([0-9.+\-Ee]+)\s*([^\s]+)",
                    line)
                if m:
                    wavelength_min_val = float(m.group(1))
                    wavelength_max_val = float(m.group(2))
                    wl_unit_token = m.group(3).rstrip(".")
                    field_x_val = float(m.group(4))
                    field_y_val = float(m.group(5))
                    field_unit_token = m.group(6).rstrip(".")

                    log.debug(
                        "Parsed wavelength range: %.6g to %.6g %s; "
                        "field: (%.6g, %.6g) %s",
                        wavelength_min_val,
                        wavelength_max_val,
                        wl_unit_token,
                        field_x_val,
                        field_y_val,
                        field_unit_token)
                    continue
                m = re.search(
                    r"Data spacing is\s+([0-9.+\-Ee]+)\s*([^\s]+)",
                    line)
                if m:
                    spacing_value = float(m.group(1))
                    spacing_token = m.group(2).rstrip(".")
                    log.debug("Found spacing: %.6g %s", spacing_value, spacing_token)
                    continue

                m = re.search(
                    r"Data area is\s+([0-9.+\-Ee]+)\s*([^\s]+)\s+wide",
                    line)
                if m:
                    area_value = float(m.group(1))
                    area_token = m.group(2).rstrip(".")
                    log.debug("Found area: %.6g %s wide", area_value, area_token)
                    continue

                m = re.search(r"Image grid size:\s*(\d+)\s*by\s*(\d+)", line)
                if m:
                    nx = int(m.group(1))
                    ny = int(m.group(2))
                    log.debug("Found grid size: %dx%d", nx, ny)
                    continue

                m = re.search(
                    r"Center point is:\s*row\s*(\d+),\s*column\s*(\d+)",
                    line)
                if m:
                    center_row = int(m.group(1))
                    center_col = int(m.group(2))
                    log.debug("Found center: row=%d, col=%d", center_row, center_col)
                    continue

                if line_stripped.startswith("Values are not normalized"):
                    in_data = True
                    log.debug("Starting to read PSF data values.")
                    continue
                continue

            if not line_stripped:
                continue

            parts = line_stripped.split()
            for p in parts:
                try:
                    data_values.append(float(p))
                except ValueError:
                    log.warning("Skipping non-numeric token in data: %r", p)

    if (
        spacing_value is None
        or spacing_token is None
        or nx is None
        or ny is None
        or center_row is None
        or center_col is None):
        raise ValueError(f"Failed to parse Zemax FFT PSF header from {path}")

    data = np.array(data_values, dtype=float)
    if data.size != nx * ny:
        raise ValueError(
            f"Unexpected number of data points in {path}: "
            f"got {data.size}, expected {nx * ny} (grid {nx}x{ny})")

    psf = data.reshape(ny, nx)
    spacing_len = make_length(spacing_value, spacing_token)
    assert spacing_len is not None


    spacing_mm: float = spacing_len.to(LengthUnit.MM)
    row0 = center_row - 1
    col0 = center_col - 1
    x_idx = np.arange(nx) - col0
    y_idx = np.arange(ny) - row0
    x_mm = x_idx * spacing_mm
    y_mm = y_idx * spacing_mm


    area_len    = make_length(area_value, area_token)
    wl_min_len  = make_length(wavelength_min_val, wl_unit_token)
    wl_max_len  = make_length(wavelength_max_val, wl_unit_token)
    field_x_len = make_length(field_x_val, field_unit_token)
    field_y_len = make_length(field_y_val, field_unit_token)

    meta = FftPsfMeta(
        spacing=spacing_len,
        area=area_len,
        nx=nx,
        ny=ny,
        center_row=center_row,
        center_col=center_col,
        wavelength_min=wl_min_len,
        wavelength_max=wl_max_len,
        field_x=field_x_len,
        field_y=field_y_len)

    log.info(
        "[Zemax FFT PSF] spacing = %s, grid = %dx%d, center = (row %d, col %d), "
        "λ=[%s, %s], field=(%s, %s)",
        spacing_len,
        nx,
        ny,
        center_row,
        center_col,
        wl_min_len if wl_min_len is not None else "n/a",
        wl_max_len if wl_max_len is not None else "n/a",
        field_x_len if field_x_len is not None else "n/a",
        field_y_len if field_y_len is not None else "n/a",
    )

    return psf, x_mm, y_mm, meta
