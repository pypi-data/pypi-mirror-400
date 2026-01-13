from dataclasses import dataclass
from typing import List, Optional
from gosti.zernike.zernike_term import ZernikeTerm

@dataclass(frozen=True)
class ZernikeReport:
    """
    Internal parser result – full info parsed from the text file.
    """
    pv_to_chief: Optional[float]
    pv_to_centroid: Optional[float]

    rms_to_chief_rays: Optional[float]
    rms_to_centroid_rays: Optional[float]

    rms_to_chief_fit: Optional[float]
    rms_to_centroid_fit: Optional[float]

    variance_rays: Optional[float]
    variance_fit: Optional[float]

    strehl_rays: Optional[float]
    strehl_fit: Optional[float]

    rms_fit_error: Optional[float]
    max_fit_error: Optional[float]

    terms: List[ZernikeTerm]