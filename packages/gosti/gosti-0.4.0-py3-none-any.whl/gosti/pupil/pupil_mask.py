from __future__ import annotations
import numpy as np
from typing import Protocol


class PupilMask(Protocol):
    def evaluate(self, x: np.ndarray, y: np.ndarray) -> np.ndarray: ...



