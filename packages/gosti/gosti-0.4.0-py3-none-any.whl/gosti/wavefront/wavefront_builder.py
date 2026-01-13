from __future__ import annotations
import numpy as np
from allytools.logger import get_logger
from allytools.units import LengthUnit
from gosti.pupil.pupil_function import PupilFunction
from gosti.wavefront.wavefront import Wavefront

log = get_logger(__name__)
class WFBuilder:

    @classmethod
    def from_pupil_function(cls, pupil_function: PupilFunction) -> Wavefront:
        wf = Wavefront(
            pupil_function=pupil_function)
        return wf
