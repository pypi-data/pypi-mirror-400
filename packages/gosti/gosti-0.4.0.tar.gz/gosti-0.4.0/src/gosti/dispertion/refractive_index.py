from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class RefractiveIndex:
    value: float

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError("Refractive index must be positive")

    def __float__(self) -> float:
        return float(self.value)

    def __repr__(self) -> str:
        return f"n={self.value:.6g}"

    def __lt__(self, other: RefractiveIndex) -> bool:
        return self.value < other.value