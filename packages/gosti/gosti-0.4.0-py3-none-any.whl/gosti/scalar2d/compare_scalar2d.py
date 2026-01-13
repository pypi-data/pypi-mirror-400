from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from allytools.logger import get_logger

log = get_logger(__name__)


NormalizeMode = Literal["max", "sum", "none"]


@dataclass
class Scalar2dMetrics:
    rmse: float
    max_abs_err: float
    corr: float
    peak1: float
    peak2: float

    def __str__(self) -> str:
        return (
            "Scalar2dMetrics(\n"
            f"  RMSE        : {self.rmse:.6g}\n"
            f"  Max |Δ|     : {self.max_abs_err:.6g}\n"
            f"  Corr        : {self.corr:.6g}\n"
            f"  Peak1       : {self.peak1:.6g}\n"
            f"  Peak2       : {self.peak2:.6g}\n"
            ")"
        )

    def __repr__(self) -> str:
        return (
            f"Scalar2dMetrics(rmse={self.rmse:.6g}, "
            f"max_abs_err={self.max_abs_err:.6g}, "
            f"corr={self.corr:.6g}, "
            f"peak1={self.peak1:.6g}, "
            f"peak2={self.peak2:.6g})"
        )


def _resample_psf_to_grid(
    psf_src: np.ndarray,
    x_src: np.ndarray,
    y_src: np.ndarray,
    x_tgt: np.ndarray,
    y_tgt: np.ndarray,
) -> np.ndarray:
    """
    Resample psf_src(x_src, y_src) to grid (x_tgt, y_tgt) via
    sequential 1D interpolation (first X, then Y).

    Assumes:
        - x_src, y_src, x_tgt, y_tgt are monotonic,
        - psf_src.shape == (len(y_src), len(x_src)).

    Values outside the range are set to 0.0.
    """
    psf_src = np.asarray(psf_src, float)
    x_src = np.asarray(x_src, float)
    y_src = np.asarray(y_src, float)
    x_tgt = np.asarray(x_tgt, float)
    y_tgt = np.asarray(y_tgt, float)

    Ny_src, Nx_src = psf_src.shape
    if Ny_src != y_src.size or Nx_src != x_src.size:
        raise ValueError(
            f"psf_src.shape {psf_src.shape} not consistent with axes: "
            f"x_src len={x_src.size}, y_src len={y_src.size}"
        )

    # 1) interpolate along X for each row (fixed y)
    tmp = np.empty((Ny_src, x_tgt.size), dtype=float)
    for j in range(Ny_src):
        tmp[j, :] = np.interp(x_tgt, x_src, psf_src[j, :], left=0.0, right=0.0)

    # 2) interpolate along Y for each column (fixed x)
    out = np.empty((y_tgt.size, x_tgt.size), dtype=float)
    for i in range(x_tgt.size):
        out[:, i] = np.interp(y_tgt, y_src, tmp[:, i], left=0.0, right=0.0)

    return out


class Scalar2Comparator:
    """
    Compare two Scalar2d fields.

    If shapes / metric grids differ, s2 is automatically resampled to the
    grid of s1 using 1D interpolation (X then Y), similar to old compare.py.
    """

    def __init__(
        self,
        s1,
        s2,
        *,
        normalize: NormalizeMode = "max",
        title1: str = "Field 1",
        title2: str = "Field 2",
    ) -> None:
        self.s1 = s1
        self.s2 = s2
        self.normalize: NormalizeMode = normalize
        self.title1 = title1
        self.title2 = title2

    @staticmethod
    def _resolve_extent(s, nx: int, ny: int) -> tuple[float, float, float, float]:
        """
        Return (xmin, xmax, ymin, ymax) for scalar field s.

        If s.extent is None, fall back to pixel indices [0, nx] × [0, ny].
        """
        if getattr(s, "extent", None) is not None:
            return tuple(map(float, s.extent))
        return (0.0, float(nx - 1), 0.0, float(ny - 1))

    @staticmethod
    def _axes_from_extent(
        extent: tuple[float, float, float, float], nx: int, ny: int
    ) -> tuple[np.ndarray, np.ndarray]:
        x_min, x_max, y_min, y_max = extent
        x = np.linspace(x_min, x_max, nx)
        y = np.linspace(y_min, y_max, ny)
        return x, y
    def compare(self) -> Scalar2dMetrics:
        """
        Compare two ScalarField2D instances and return scalar metrics.

        If shapes or metric grids differ, s2 is resampled onto the metric
        grid of s1 using sequential 1D interpolation (X then Y).
        """
        s1, s2 = self.s1, self.s2
        log.debug("Starting Scalar2d comparison...shape1=%s shape2-%s", s1.values.shape, s2.values.shape)
        ny1, nx1 = s1.values.shape
        ny2, nx2 = s2.values.shape
        x1 = s1.x_coords  # shape (nx1,)
        y1 = s1.y_coords  # shape (ny1,)
        x2 = s2.x_coords  # shape (nx2,)
        y2 = s2.y_coords  # shape (ny2,)

        same_x_shape = x1.shape == x2.shape
        same_y_shape = y1.shape == y2.shape


        if same_x_shape:
            allclose_x = np.allclose(x1, x2, rtol=1e-6, atol=1e-9)
            max_dx = float(np.max(np.abs(x1 - x2)))
        else:
            allclose_x = False
            max_dx = float("nan")

        if same_y_shape:
            allclose_y = np.allclose(y1, y2, rtol=1e-6, atol=1e-9)
            max_dy = float(np.max(np.abs(y1 - y2)))
        else:
            allclose_y = False
            max_dy = float("nan")

        log.debug(
            "nx1=%d nx2=%d ny1=%d ny2=%d same_x_shape=%s same_y_shape=%s "
            "allclose_x=%s allclose_y=%s max|Δx|=%.3e max|Δy|=%.3e",
            nx1, nx2, ny1, ny2,
            same_x_shape, same_y_shape,
            allclose_x, allclose_y,
            max_dx, max_dy,
        )

        # Decide whether we need to resample s2 onto s1 grid
        need_resample = (
                (nx1 != nx2)
                or (ny1 != ny2)
                or (not np.allclose(x1, x2))
                or (not np.allclose(y1, y2)))


        if need_resample:
            log.debug("Scalar2d grids differ → resample second field to grid of first "
                "(shape1=%s, shape2=%s)", s1.values.shape, s2.values.shape)
            p1 = s1.values.astype(float).copy()
            p2 = _resample_psf_to_grid(
                psf_src=s2.values,
                x_src=x2,
                y_src=y2,
                x_tgt=x1,
                y_tgt=y1)
        else:
            log.debug("Scalar2d grids match; no resampling required.")
            p1 = s1.values.astype(float).copy()
            p2 = s2.values.astype(float).copy()
        log.debug("Applying normalization: %s", self.normalize)

        if self.normalize == "max":
            m1, m2 = p1.max(), p2.max()
            p1 /= m1 if m1 != 0 else 1.0
            p2 /= m2 if m2 != 0 else 1.0
            log.debug("Normalized by max: max1=%.6g, max2=%.6g", m1, m2)

        elif self.normalize == "sum":
            s_1, s_2 = p1.sum(), p2.sum()
            p1 /= s_1 if s_1 != 0 else 1.0
            p2 /= s_2 if s_2 != 0 else 1.0
            log.debug("Normalized by sum: sum1=%.6g, sum2=%.6g", s_1, s_2)

        elif self.normalize == "none":
            log.debug("No normalization applied.")

        else:
            raise ValueError(f"Unknown normalize='{self.normalize}'. Use 'max', 'sum', or 'none'.")
        diff = p1 - p2
        mse = np.mean(diff**2)
        rmse = float(np.sqrt(mse))
        max_abs_err = float(np.max(np.abs(diff)))

        # Robust correlation (avoid NaN if one field is constant)
        a = p1.ravel()
        b = p2.ravel()
        if np.std(a) == 0.0 or np.std(b) == 0.0:
            corr = float("nan")
        else:
            corr = float(np.corrcoef(a, b)[0, 1])

        metrics = Scalar2dMetrics(
            rmse=rmse,
            max_abs_err=max_abs_err,
            corr=corr,
            peak1=float(p1.max()),
            peak2=float(p2.max()))

        log.debug("Scalar2d comparison completed. corr=%.6g, rmse=%.6g, max|Δ|=%.6g",
                  metrics.corr, metrics.rmse, metrics.max_abs_err)
        return metrics
