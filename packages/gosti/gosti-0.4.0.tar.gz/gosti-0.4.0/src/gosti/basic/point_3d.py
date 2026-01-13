from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import TYPE_CHECKING, Union
from allytools.units import Length

if TYPE_CHECKING:
    from gosti.basic.vector_3d import Vector3D

@dataclass(frozen=True, slots=True)
class Point3D:
    """3D point (position) with Length units."""
    x: Length
    y: Length
    z: Length

    def as_mm(self) -> np.ndarray:
        return np.array([float(self.x.value_mm), float(self.y.value_mm), float(self.z.value_mm)], dtype=float)

    def __add__(self, v: "Vector3D") -> "Point3D":
        return Point3D(self.x + v.x, self.y + v.y, self.z + v.z)

    def __sub__(self, other: Union["Point3D", "Vector3D"]) -> Union["Vector3D", "Point3D"]:
        from gosti.basic.vector_3d import Vector3D
        if isinstance(other, Point3D):
            return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)
        return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def distance_to(self, other: "Point3D") -> Length:
        return (self - other).norm()  # type: ignore[return-value]

    def __str__(self) -> str:
        return f"Point3D(x={self.x}, y={self.y}, z={self.z})"