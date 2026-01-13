from dataclasses import dataclass
from pathlib import Path
import logging
import numpy as np
from gosti.fft_psf.compute_fft_psf import compute_fft_psf
from gosti.scalar2d.scalar_field2d import ScalarField2D  # adjust path if needed

log = logging.getLogger(__name__)
@dataclass
class FftPsf:
    field: ScalarField2D
    wavelength_nm: float
    focal_length_mm: float
    field_x_img_mm: float | None = None
    field_y_img_mm: float | None = None
    exit_pupil_diameter_mm: float | None = None
    exit_pupil_position_mm: float | None = None


    @property
    def raw_psf(self) -> np.ndarray:
        return self.field.values

    @classmethod
    def from_zernike(
        cls,
        *,
        coefficients: np.ndarray,
        n_coef: int,
        wavelength_mm: float,
        exit_pupil_diameter_mm: float,
        exit_pupil_position_mm: float,
        focal_length_mm: float,
        grid_size: int,
        pad_factor: int = 4,
        field_x_img_mm: float | None = None,
        field_y_img_mm: float | None = None,
    ) -> "FftPsf":
        """
        Compute FFT PSF from Zernike coefficients and wrap it in FftPsf.
        """

        log.debug(
            "[FftPsf] from_zernike: N_modes=%d, λ=%.3f nm, D_pupil=%.3f mm, "
            "f=%.3f mm, grid=%d, pad=%d",
            n_coef,
            wavelength_mm,
            exit_pupil_diameter_mm,
            focal_length_mm,
            grid_size,
            pad_factor,
        )

        field = compute_fft_psf(
            coefficients=coefficients,
            n_coef=n_coef,
            wavelength_mm=wavelength_mm,
            exit_pupil_diameter_mm=exit_pupil_diameter_mm,
            exit_pupil_position_mm=exit_pupil_position_mm,
            focal_length_mm=focal_length_mm,
            grid_size=grid_size,
            pad_factor=pad_factor,
            field_x_img_mm=field_x_img_mm,
            field_y_img_mm=field_y_img_mm,
        )

        log.debug(
            "[FftPsf] from_zernike: PSF field shape=%s, extent=%s",
            field.shape,
            field.extent_mm,
        )

        return cls(
            field=field,
            wavelength_nm=wavelength_mm,
            focal_length_mm=focal_length_mm,
            field_x_img_mm=field_x_img_mm,
            field_y_img_mm=field_y_img_mm,
            exit_pupil_diameter_mm=exit_pupil_diameter_mm,
            exit_pupil_position_mm=exit_pupil_position_mm,
        )

    def save_psf_npz(self, path: Path) -> None:
        np.savez(
            path,
            psf=self.field.values,
            x_mm=self.field.x_coords,
            y_mm=self.field.y_coords,
            wavelength_nm=self.wavelength_nm,
            exit_pupil_diameter_mm=self.exit_pupil_diameter_mm,
            focal_length_mm=self.focal_length_mm,
        )
        log.debug("[FftPsf] PSF saved to NPZ: %s", path)

    def save_psf_txt(self, path: Path) -> None:
        psf = self.field.values
        x_mm = self.field.x_coords
        y_mm = self.field.y_coords
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
