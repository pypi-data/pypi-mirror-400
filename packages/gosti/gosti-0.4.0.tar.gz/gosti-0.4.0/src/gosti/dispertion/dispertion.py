from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod
from gosti.wavelength import Wavelength


class WavelengthOutOfRange(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class Dispersion(ABC):
    wl_min: Wavelength
    wl_max: Wavelength
    strict_range: bool = True

    def n(self, wavelength: Wavelength) -> float:
        """Public API: range check + formula."""
        if self.strict_range and not (self.wl_min <= wavelength <= self.wl_max):
            raise WavelengthOutOfRange(
                f"Wavelength {wavelength} outside "
                f"[{self.wl_min}, {self.wl_max}]"
            )
        return self._n_formula(wavelength)

    @abstractmethod
    def _n_formula(self, wavelength: Wavelength) -> float:
        """Concrete dispersion formula (no checks here)."""
        ...