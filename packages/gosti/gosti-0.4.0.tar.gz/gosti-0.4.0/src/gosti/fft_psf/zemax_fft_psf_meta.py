from dataclasses import dataclass
from allytools.units import Length

@dataclass(frozen=True)
class FftPsfMeta:
    spacing: Length
    area: Length | None
    nx: int
    ny: int
    center_row: int
    center_col: int

    wavelength_min: Length | None
    wavelength_max: Length | None

    field_x: Length | None
    field_y: Length | None
