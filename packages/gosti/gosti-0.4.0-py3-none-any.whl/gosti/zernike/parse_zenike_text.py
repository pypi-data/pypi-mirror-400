from typing import List, Optional
from gosti.zernike.zernike_term import ZernikeTerm
from gosti.zernike.zernike_report import ZernikeReport
from gosti.zernike.zernike_aid import parse_scalar

def parse_zernike_text(text: str) -> ZernikeReport:
    """
    Parse a full Zernike Standard Coefficients text block into ZernikeReport.
    Handles:
      - Peak to Valley (to chief / centroid)
      - From integration of the rays: RMS, variance, Strehl
      - From integration of the fitted coefficients: RMS, variance, Strehl
      - RMS fit error, Maximum fit error
      - All 'Z n <coeff> : <label>' lines
    """
    text = text.replace("\x00", "")
    lines = text.splitlines()

    pv_to_chief = pv_to_centroid = None
    rms_to_chief_rays = rms_to_centroid_rays = None
    rms_to_chief_fit = rms_to_centroid_fit = None
    variance_rays = variance_fit = None
    strehl_rays = strehl_fit = None
    rms_fit_error = max_fit_error = None

    terms: List[ZernikeTerm] = []

    # Track which block we are in: None / "rays" / "fit"
    section: Optional[str] = None

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        # --- Section headers ---
        if "From integration of the rays" in line:
            section = "rays"
            continue

        if "From integration of the fitted coefficients" in line:
            section = "fit"
            continue

        # --- Peak to valley ---
        if "Peak to Valley (to chief)" in line:
            pv_to_chief = parse_scalar(line)
            continue

        if "Peak to Valley (to centroid)" in line:
            pv_to_centroid = parse_scalar(line)
            continue

        # --- Scalars inside 'rays' section ---
        if section == "rays":
            if "RMS (to chief)" in line:
                rms_to_chief_rays = parse_scalar(line)
                continue
            if "RMS (to centroid)" in line:
                rms_to_centroid_rays = parse_scalar(line)
                continue
            if line.startswith("Variance"):
                variance_rays = parse_scalar(line)
                continue
            if line.startswith("Strehl Ratio"):
                strehl_rays = parse_scalar(line)
                continue

        # --- Scalars inside 'fit' section ---
        if section == "fit":
            if "RMS (to chief)" in line:
                rms_to_chief_fit = parse_scalar(line)
                continue
            if "RMS (to centroid)" in line:
                rms_to_centroid_fit = parse_scalar(line)
                continue
            if line.startswith("Variance"):
                variance_fit = parse_scalar(line)
                continue
            if line.startswith("Strehl Ratio"):
                strehl_fit = parse_scalar(line)
                continue

        # --- Global fit error lines (outside sections) ---
        if line.startswith("RMS fit error"):
            rms_fit_error = parse_scalar(line)
            continue

        if line.startswith("Maximum fit error"):
            max_fit_error = parse_scalar(line)
            continue

        # --- Zernike coefficient lines ---
        parts = line.split()
        if len(parts) >= 3 and parts[0] == "Z":
            try:
                idx = int(parts[1])
                coeff = float(parts[2])
            except ValueError:
                continue

            label = ""
            if ":" in line:
                label = line.split(":", 1)[1].strip()

            terms.append(ZernikeTerm(index=idx, coefficient=coeff, label=label))

    return ZernikeReport(
        pv_to_chief=pv_to_chief,
        pv_to_centroid=pv_to_centroid,
        rms_to_chief_rays=rms_to_chief_rays,
        rms_to_centroid_rays=rms_to_centroid_rays,
        rms_to_chief_fit=rms_to_chief_fit,
        rms_to_centroid_fit=rms_to_centroid_fit,
        variance_rays=variance_rays,
        variance_fit=variance_fit,
        strehl_rays=strehl_rays,
        strehl_fit=strehl_fit,
        rms_fit_error=rms_fit_error,
        max_fit_error=max_fit_error,
        terms=terms,
    )
