import numpy as np
from allytools.logger import get_logger
from scipy.interpolate import RegularGridInterpolator
from gosti.scalar2d.scalar_field2d import ScalarField2D

log = get_logger(__name__)
def resample_scalar2d(source: ScalarField2D, target: ScalarField2D) -> ScalarField2D:
    """
    Resample 'source' field onto the grid defined by 'target'.
    Returns a new ScalarField2D with target's geometry and interpolated values.
    """
    log.debug("Starting Scalar2d resample: source(shape=%s, extent=%s) -> "
        "target(shape=%s, extent=%s)",
        source.shape, source.extent, target.shape, target.extent)
    try:
        x_min_um_s, x_max_um_s, y_min_um_s, y_max_um_s = map(float, source.extent_um)
    except Exception as e:
        raise ValueError(f"Invalid source.extent_um: {source.extent_um}") from e
    ny_s, nx_s = source.shape
    xs = np.linspace(x_min_um_s, x_max_um_s, nx_s)
    ys = np.linspace(y_min_um_s, y_max_um_s, ny_s)
    log.debug("Source extent_um = %s", source.extent_um)
    log.debug("Source grid       = (%d, %d) samples", ny_s, nx_s)

    interp = RegularGridInterpolator(
        (ys, xs),
        source.values,
        bounds_error=False,
        fill_value=0.0)
    try:
        x_min_um_t, x_max_um_t, y_min_um_t, y_max_um_t = map(float, target.extent_um)
    except Exception as e:
        raise ValueError(f"Invalid target.extent_um: {target.extent_um}") from e
    ny_t, nx_t = target.shape
    xt = np.linspace(x_min_um_t, x_max_um_t, nx_t)
    yt = np.linspace(y_min_um_t, y_max_um_t, ny_t)
    log.debug("Target extent_um = %s", target.extent_um)
    log.debug("Target grid       = (%d, %d) samples", ny_t, nx_t)

    Xg, Yg = np.meshgrid(xt, yt)  # shape (ny_t, nx_t)
    points = np.stack([Yg.ravel(), Xg.ravel()], axis=-1)

    log.debug("Interpolating Scalar2d...")
    data_interp = interp(points).reshape(ny_t, nx_t)
    log.debug("Interpolation complete. Output shape = %s", data_interp.shape)

    result = ScalarField2D(
        values=data_interp,
        min_x=target.min_x,
        min_y=target.min_y,
        dx=target.dx,
        dy=target.dy)

    log.info(
        "Resampled Scalar2d created: shape=%s, extent=%s",
        result.shape,
        result.extent)
    return result
