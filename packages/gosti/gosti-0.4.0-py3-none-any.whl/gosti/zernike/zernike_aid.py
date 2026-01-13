import tempfile
import re
from pathlib import Path
from typing import Optional

def get_zernike_text_from_result(result) -> str:
    """
    Use result.GetTextFile(filename) and return the text as a Python str.
    Handles UTF-16 OpticStudio exports and strips NULL bytes.
    """
    tmp_path = Path(tempfile.gettempdir()) / "zemax_zernike_tmp.txt"
    ok = result.GetTextFile(str(tmp_path))
    if not ok:
        raise RuntimeError("GetTextFile(...) returned False")
    data = tmp_path.read_bytes()
    try:
        text = data.decode("utf-16") # OpticStudio exports UTF-16LE with BOM
    except UnicodeError:
        text = data.decode("utf-8", errors="ignore")
    text = text.replace("\x00", "") # CRITICAL: remove NUL bytes that appear in mis-decoded UTF-16
    try:
        tmp_path.unlink()
    except OSError:
        pass

    return text

_number_re = re.compile(r"[+-]?\d*\.?\d+(?:[eE][+-]?\d+)?")

def parse_scalar(line: str) -> Optional[float]:
    """
    Extract first float after ':' from a line like:
        'RMS (to chief) : 1.234567 waves'
    """
    if ":" not in line:
        return None
    part = line.split(":", 1)[1]
    m = _number_re.search(part)
    if not m:
        return None
    try:
        return float(m.group())
    except ValueError:
        return None
