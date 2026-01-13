from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import TYPE_CHECKING, Union
from allytools.units import Length

if TYPE_CHECKING:
    from gosti.basic.vector_2d import Vector2D


@dataclass(frozen=True, slots=True)
class Point2D:
    """2D point (position) with Length units."""
    x: Length
    y: Length

    def as_mm(self) -> np.ndarray:
        return np.array([float(self.x.value_mm), float(self.y.value_mm)], dtype=float)

    def __add__(self, v: "Vector2D") -> "Point2D":
        return Point2D(self.x + v.x, self.y + v.y)

    def __sub__(self, other: Union["Point2D", "Vector2D"]) -> Union["Vector2D", "Point2D"]:
        from gosti.basic.vector_2d import Vector2D
        if isinstance(other, Point2D):
            return Vector2D(self.x - other.x, self.y - other.y)
        return Point2D(self.x - other.x, self.y - other.y)

    def distance_to(self, other: Point2D) -> Length:
        return (self - other).norm()

    def __str__(self) -> str:
        return f"Point2D(x={self.x}, y={self.y})"