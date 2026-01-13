import math
import numpy as np
from allytools.logger import get_logger
from gosti.pupil.pupil_grid import PupilGrid

log = get_logger(__name__)
class ZernikeBasis:

    # Convert (n, m) → Noll/Zemax 1-based index j
    @staticmethod
    def _noll_j_from_nm(n: int, m: int) -> int:
        """
        Convert (n, m) → Noll / Zemax Standard index j = 1,2,...

        Validity rules:
        - |m| <= n
        - (n - m) must be even
        """

        log.trace(f" Computing Noll index for (n={n}, m={m}).")

        if abs(m) > n or ((n - m) % 2) != 0:
            raise ValueError(f"Invalid (n,m) for Zernike: n={n}, m={m}")

        a = n * (n + 1) // 2 + abs(m)
        n_mod = n % 4

        if (m > 0 and n_mod in (0, 1)) or (m < 0 and n_mod in (2, 3)):
            offset = 0
        else:
            offset = 1

        j = a + offset
        log.trace(f" Noll index j={j} for (n={n}, m={m}).")

        return j


    # Convert Zemax Standard index j → (n, m)
    @staticmethod
    def zemax_index_to_nm(j: int) -> tuple[int, int]:
        """
        Convert j = 1..N (Zemax Zernike Standard Coefficients)
        → (n, m) following the Noll/OpticStudio convention.
        """

        log.trace(f" Converting Zemax index j={j} → (n, m).")

        j = int(j)

        # n up to 20 easily covers all 231 Zemax terms
        for n in range(0, 20):
            for m in range(-n, n + 1, 2):
                if ZernikeBasis._noll_j_from_nm(n, m) == j:
                    log.trace(f" j={j} maps to (n={n}, m={m}).")
                    return n, m

        raise ValueError(f"Cannot map Zernike index j={j} to (n,m)")


    # OSA/ANSI mapping j(0-based) → (n,m)
    @staticmethod
    def osa_index_to_nm(j: int) -> tuple[int, int]:
        """
        OSA/ANSI mapping (0-based index):
            j = (n(n+2) + m) / 2
        """

        n = int(math.floor((math.sqrt(8*j + 1) - 1) / 2))
        m = int(2*j - n*(n + 2))
        log.trace(f"OSA index j={j} → (n={n}, m={m}).")
        return n, m

    # Radial polynomial R_n^{|m|}
    @staticmethod
    def radial_poly(n: int, m: int, rho: np.ndarray) -> np.ndarray:
        """
        Compute the radial Zernike polynomial R_n^{|m|}(rho)
        using the OSA/ANSI definition.
        """

        log.trace(f"Computing radial polynomial R_{n}^{{|{m}|}} for rho grid.")
        m = abs(m)
        R = np.zeros_like(rho)
        # Standard OSA radial sum
        for k in range((n - m)//2 + 1):
            num = math.factorial(n - k)
            den = (math.factorial(k)
                * math.factorial((n + m)//2 - k)
                * math.factorial((n - m)//2 - k))
            c = ((-1)**k) * num / den
            R += c * rho**(n - 2*k)
        return R

    def build_basis(self, n_modes: int, grid: PupilGrid) -> np.ndarray:
        log.trace(f"Building Zernike with {n_modes} modes.")
        grid_size = grid.grid_size
        basis = np.zeros((n_modes, grid_size, grid_size), dtype=float)
        for k in range(1, n_modes + 1):
            j = k
            n_order, m_order = self.zemax_index_to_nm(j)
            log.trace(f"Mode k={k}: using (n_order={n_order}, m_order={m_order}).")
            radial = self.radial_poly(n_order, m_order, grid.rho)
            if m_order == 0:
                z = math.sqrt(n_order + 1) * radial
            elif m_order > 0:
                z = math.sqrt(2 * (n_order + 1)) * radial * np.cos(m_order * grid.phi)
            else:
                z = math.sqrt(2 * (n_order + 1)) * radial * np.sin(-m_order * grid.phi)
            basis[k - 1] = z * grid.mask
        basis_flat = basis.reshape(n_modes, -1)
        log.debug("Basis assembled. Shape=%s", basis_flat.shape)
        return basis_flat



