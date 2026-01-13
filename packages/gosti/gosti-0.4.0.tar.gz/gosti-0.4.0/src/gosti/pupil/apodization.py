import numpy as np
from typing import Protocol, runtime_checkable
from gosti.pupil.pupil_grid import PupilGrid


from enum import Enum, auto

class ApodizationType(Enum):
    UNIFORM = auto()
    GAUSSIAN = auto()
    COSINE_CUBED = auto()
    USER_DEFINED = auto()

@runtime_checkable
class Apodization(Protocol):
    @property
    def kind(self) -> ApodizationType: ...

    def amplitude(self, grid: PupilGrid) -> np.ndarray: ...