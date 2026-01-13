from dataclasses import dataclass
from typing import Tuple, Optional
import numpy as np
from numpy.typing import NDArray
import matplotlib.pyplot as plt
from allytools.units import Length, LengthUnit
from imagera.plotter import PltScalar2d, PlotParameters, CMaps
from imagera.image import ImageBundle


@dataclass(slots=True)
class ScalarField2D:
    """
    Minimal independent 2D scalar array with metric axis definition.

    Parameters
    ----------
    values : 2D ndarray
        The scalar field values.
    min_x, min_y : Length
        Coordinate of the (0,0) pixel.
    dx, dy : Length
        Pixel pitch in X and Y.
    """
    values: NDArray[np.float64]
    min_x: Length
    min_y: Length
    dx: Length
    dy: Length

    @property
    def shape(self) -> Tuple[int, int]:
        ny, nx = self.values.shape
        return ny, nx

    @property
    def ny(self) -> int:
        return self.values.shape[0]

    @property
    def nx(self) -> int:
        return self.values.shape[1]

    @property
    def x_max(self) -> Length:
        unit = self.min_x.unit
        dx_in_unit = self.dx.to(unit)
        min_x_in_unit = self.min_x.to(unit)
        x_max_value = min_x_in_unit + (self.nx - 1) * dx_in_unit
        return Length(x_max_value, unit)

    @property
    def y_max(self) -> Length:
        unit = self.min_y.unit
        dy_in_unit = self.dy.to(unit)
        min_y_in_unit = self.min_y.to(unit)
        y_max_value = min_y_in_unit + (self.ny - 1) * dy_in_unit
        return Length(y_max_value, unit)

    @property
    def extent(self) -> Tuple[Length, Length, Length, Length]:
        return self.min_x, self.x_max, self.min_y, self.y_max

    @property
    def extent_um(self) -> Tuple[float, float, float, float]:
        return (
            self.min_x.to(LengthUnit.UM),
            self.x_max.to(LengthUnit.UM),
            self.min_y.to(LengthUnit.UM),
            self.y_max.to(LengthUnit.UM))

    @property
    def x_coords(self) -> NDArray[np.float64]:
        """
        1D array of x-coordinates [mm] for each column index.
        """
        return (self.min_x.value_mm
            + self.dx.value_mm * np.arange(self.nx, dtype=np.float64))

    @property
    def y_coords(self) -> NDArray[np.float64]:
        """
        1D array of y-coordinates [mm] for each row index.
        """
        return (self.min_y.value_mm
            + self.dy.value_mm * np.arange(self.ny, dtype=np.float64))

    def x(self, ix: int) -> Length:
        return self.min_x + self.dx * ix

    def y(self, iy: int) -> Length:
        return self.min_y + self.dy * iy

    @property
    def value_min(self) -> float:
        return float(np.nanmin(self.values))

    @property
    def value_max(self) -> float:
        return float(np.nanmax(self.values))

    def z(self, ix: int, iy: int) -> float:
        return float(self.values[iy, ix])

    def crop(
        self,
        *,
        iy_min: int,
        iy_max: int,
        ix_min: int,
        ix_max: int,
    ) -> "ScalarField2D":
        """
        Return a cropped view of the field as a new ScalarField2D.

        Indices use NumPy semantics: [iy_min:iy_max, ix_min:ix_max),
        i.e. iy_max and ix_max are exclusive.
        """
        if not (0 <= iy_min <= iy_max <= self.ny):
            raise ValueError(f"Invalid y indices: iy_min={iy_min}, iy_max={iy_max}, ny={self.ny}")
        if not (0 <= ix_min <= ix_max <= self.nx):
            raise ValueError(f"Invalid x indices: ix_min={ix_min}, ix_max={ix_max}, nx={self.nx}")

        cropped_values = self.values[iy_min:iy_max, ix_min:ix_max]
        new_min_x = self.min_x + self.dx * ix_min
        new_min_y = self.min_y + self.dy * iy_min

        return ScalarField2D(
            values=cropped_values,
            min_x=new_min_x,
            min_y=new_min_y,
            dx=self.dx,
            dy=self.dy)

    def get_image_bundle(
            self,
            plot_params: Optional[PlotParameters] = None,
            *,
            plot_label: Optional[str] = None,
            **overrides):

        scalar2d = PltScalar2d(
            self.values,
            params=plot_params,
            extent=self.extent,
            hide_ticks=False,
            show_lattice=True,
            lattice_color=(1, 1, 1, 0.4),
            plot_label=plot_label,
            **overrides)

        array_image = scalar2d.render()
        return ImageBundle(array_image)

    def simple_plot(self, *, cmap="viridis", with_colorbar=True, ax=None):
        if ax is None:
            fig, ax = plt.subplots()

        im = ax.imshow(
            self.values,
            extent=self.extent_um,
            origin="lower",
            cmap=cmap,
            interpolation="nearest",
            aspect="equal")

        if with_colorbar:
            plt.colorbar(im, ax=ax)
        ax.set_xlabel("x [mm]")
        ax.set_ylabel("y [mm]")
        return ax, im

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(\n"
            f"  shape      = {self.ny} × {self.nx},\n"
            f"  x range    = [{self.min_x.to(LengthUnit.UM):.4f} … {self.x_max.to(LengthUnit.UM):.4f}] µm dx = {self.dx.to(LengthUnit.UM):.4f} µm,\n"
            f"  y range    = [{self.min_y.to(LengthUnit.UM):.4f} … {self.y_max.to(LengthUnit.UM):.4f}] µm dy = {self.dy.to(LengthUnit.UM):.4f} µm,\n"
            f"  value min  = {self.value_min:.6g},\n"
            f"  value max  = {self.value_max:.6g}\n"
            f")"
        )