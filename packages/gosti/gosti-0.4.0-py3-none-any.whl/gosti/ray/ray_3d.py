from __future__ import annotations
from dataclasses import dataclass
from allytools.units import Length
from gosti.basic.point_3d import Point3D
from gosti.basic.unit_vector3d import UnitVector3D


@dataclass(frozen=True, slots=True)
class Ray3D:
    """Geometric ray: origin point + unit direction.

    Conventions:
      - direction is unitless (direction cosines)
      - 'require_forward' logic can be enforced when building the UnitVector3D
    """
    origin: Point3D
    direction: UnitVector3D

    def at(self, s: Length) -> Point3D:
        """Point at distance s along the ray."""
        return self.origin + self.direction.to_vector(s)

    def advance(self, s: Length) -> Ray3D:
        """Return a new ray advanced by distance s."""
        return Ray3D(origin=self.at(s), direction=self.direction)
