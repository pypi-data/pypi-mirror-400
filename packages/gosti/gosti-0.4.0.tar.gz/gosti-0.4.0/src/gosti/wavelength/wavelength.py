from __future__ import annotations
from typing import cast
from allytools.units.length import Length
from allytools.units.length_unit import LengthUnit

class Wavelength(Length):
    def __init__(self, value: float, unit: LengthUnit = LengthUnit.NM):
        value_mm = float(value) * unit.factor
        value_nm = value_mm / LengthUnit.NM.factor
        super().__init__(value_nm, LengthUnit.NM)

    @property
    def value_nm(self) -> float:
        return self.to(LengthUnit.NM)

    def _with_value_mm(self, value_mm: float) -> Wavelength:
        value_nm = value_mm / LengthUnit.NM.factor
        return Wavelength(value_nm)

    def _with_value_nm(self, value_nm: float) -> Wavelength:
        return Wavelength(value_nm)

    def __add__(self, other: object) -> Wavelength:
        if type(other) is not Wavelength:
            return NotImplemented
        other_wl = cast(Wavelength, other)
        return self._with_value_mm(self.value_mm + other_wl.value_mm)

    def __sub__(self, other: object) -> Wavelength:
        if type(other) is not Wavelength:
            return NotImplemented
        other_wl = cast(Wavelength, other)
        return self._with_value_mm(self.value_mm - other_wl.value_mm)
