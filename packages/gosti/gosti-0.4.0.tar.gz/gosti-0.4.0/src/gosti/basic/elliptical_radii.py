from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class EllipseRadii:
    r_tan: float
    r_sag: float