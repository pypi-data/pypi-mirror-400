from dataclasses import dataclass

@dataclass(frozen=True)
class ZernikeTerm:
    index: int
    coefficient: float
    label: str
