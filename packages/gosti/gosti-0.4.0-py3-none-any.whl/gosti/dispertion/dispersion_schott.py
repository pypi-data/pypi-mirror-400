from __future__ import annotations
from dataclasses import dataclass
from gosti.wavelength import Wavelength

@dataclass(frozen=True, slots=True)
class SchottDispersion:
    # n^2 = a0 + a1*λ^2 + a2*λ^-2 + a3*λ^-4 + a4*λ^-6 + a5*λ^-8
    a0: float
    a1: float
    a2: float
    a3: float
    a4: float
    a5: float
    wl_min: Wavelength
    wl_max: Wavelength
    strict_range: bool = True  # если False — можно не падать, а просто считать

    def n(self, wavelength: Wavelength) -> float:
        if self.strict_range and not (self.wl_min <= wavelength <= self.wl_max):
            raise WavelengthOutOfRange(
                f"Wavelength {wavelength.value_nm:.3f} nm is outside "
                f"[{self.wl_min.value_nm:.3f}, {self.wl_max.value_nm:.3f}] nm"
            )

        lam = _as_um(wavelength)  # Schott обычно в μm
        lam2 = lam * lam
        inv2 = 1.0 / lam2
        inv4 = inv2 * inv2
        inv6 = inv4 * inv2
        inv8 = inv4 * inv4

        n2 = (
            self.a0
            + self.a1 * lam2
            + self.a2 * inv2
            + self.a3 * inv4
            + self.a4 * inv6
            + self.a5 * inv8
        )
        if n2 <= 0:
            raise ValueError(f"Schott formula produced non-positive n^2={n2} at {lam} um")
        return float(n2 ** 0.5)