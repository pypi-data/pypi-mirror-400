from __future__ import annotations
from abc import ABC, abstractmethod
import numpy as np

class Surface3d(ABC):

    @abstractmethod
    def intersect(self, ray_o: np.ndarray, ray_d: np.ndarray) -> float | None:
        """
        Return distance t such that ray_o + t * ray_d lies on the surface,
        or None if no intersection.
        """

    @abstractmethod
    def normal_at(self, p: np.ndarray) -> np.ndarray:
        """
        Return unit surface normal at point p (3,).
        MUST be implemented.
        """

    @abstractmethod
    def point_at_params(self, u: float, v: float) -> np.ndarray:
        """
        Optional but very useful: parametric surface point.
        """

    @abstractmethod
    def normal_at_params(self, u: float, v: float) -> np.ndarray:
        """
        Parametric normal (often cheaper & more stable).
        """
