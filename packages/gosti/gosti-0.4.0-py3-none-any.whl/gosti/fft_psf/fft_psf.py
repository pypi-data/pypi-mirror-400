from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from typing import  Optional
from allytools.units import Length, LengthUnit
from allytools.logger import get_logger
from gosti.fft_psf.compute_fft_psf import compute_fft_psf
from gosti.scalar2d.scalar_field2d import ScalarField2D
from gosti.wavelength import Wavelength

log = get_logger(__name__)
@dataclass
class FftPsf:
    scalar2d: ScalarField2D
    wavelength: Wavelength
    field_x: Length | None = None
    field_y: Length | None = None

    @property
    def raw_psf(self) -> np.ndarray:
        return self.scalar2d.values

    @classmethod
    def from_zernike(
        cls,
        *,
        coefficients: np.ndarray,
        wavelength: Wavelength,
        exit_pupil_diameter: Length,
        exit_pupil_position: Length,
        grid_size: int,
        pad_factor: int = 4,
        field_x_img: Optional[Length] = None,
        field_y_img: Optional[Length] = None) -> FftPsf:

        field = compute_fft_psf(
            coefficients=coefficients,
            wavelength=wavelength,
            exit_pupil_diameter=exit_pupil_diameter,
            exit_pupil_position=exit_pupil_position,
            grid_size=grid_size,
            pad_factor=pad_factor,
            field_x_img=field_x_img,
            field_y_img=field_y_img)

        log.debug("[FftPsf] from_zernike: PSF field shape=%s, extent=%s", field.shape,field.extent_um)
        return cls(
            scalar2d=field,
            wavelength=wavelength,
            field_x=field_x_img,
            field_y=field_y_img)

    def save_psf_npz(self, path: Path) -> None:
        np.savez(
            path,
            psf=self.scalar2d.values,
            x_mm=self.scalar2d.x_coords,
            y_mm=self.scalar2d.y_coords,
            wavelength_nm=self.wavelength.value_mm)
        log.debug("[FftPsf] PSF saved to NPZ: %s", path)

    def save_psf_txt(self, path: Path) -> None:
        psf = self.scalar2d.values
        x_mm = self.scalar2d.x_coords
        y_mm = self.scalar2d.y_coords
        H, W = psf.shape

        with path.open("w", encoding="utf-8") as f:
            f.write("# PSF export\n")
            f.write(f"# Nx={W} Ny={H}\n")
            f.write("# x_mm:\n")
            f.write(" ".join(f"{v:.9e}" for v in x_mm) + "\n")
            f.write("# y_mm:\n")
            f.write(" ".join(f"{v:.9e}" for v in y_mm) + "\n")
            f.write("# psf[y,x]:\n")
            for j in range(H):
                f.write(" ".join(f"{psf[j, i]:.9e}" for i in range(W)) + "\n")
        log.debug("[FftPsf] PSF (ASCII) saved to TXT: %s", path)

    def get_crop(self, k:int, airy_radius:Length)-> "FftPsf":
        airy_radius_dx = airy_radius / self.scalar2d.dx
        log.debug(
            "Crop for %d airy radii (Airy radius = %.3f [um], or %d times from  dx=%.3f [um]",
            k,
            airy_radius.to(LengthUnit.UM),
            airy_radius_dx,
            self.scalar2d.dx.to(LengthUnit.UM))
        half_win = int(k * airy_radius_dx)
        h, w = self.scalar2d.shape
        cy, cx = h // 2, w // 2
        iy_min = cy - half_win
        iy_max = cy + half_win + 1
        ix_min = cx - half_win
        ix_max = cx + half_win + 1
        psf_crop = self.scalar2d.crop(
            iy_min=iy_min,
            iy_max=iy_max,
            ix_min=ix_min,
            ix_max=ix_max)
        return FftPsf(scalar2d=psf_crop, wavelength=self.wavelength, field_x=self.field_x, field_y=self.field_y)