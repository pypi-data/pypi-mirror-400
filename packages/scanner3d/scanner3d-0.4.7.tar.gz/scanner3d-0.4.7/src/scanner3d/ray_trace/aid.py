from __future__ import annotations
import  math
from typing import Tuple, Optional, Any

def pol_to_components(pol: Optional[Tuple[float, float, float, float]]) -> Tuple[float, float, float, float, float, float]:
    if pol is None:
        return 1.0, 0.0, 0.0, 0.0, 0.0, 0.0
    Ex, Ey, phaX_deg, phaY_deg = pol
    phiX = math.radians(phaX_deg)
    phiY = math.radians(phaY_deg)
    return (
        Ex * math.cos(phiX), Ex * math.sin(phiX),
        Ey * math.cos(phiY), Ey * math.sin(phiY),
        0.0, 0.0
    )

def accept_default(rec: Any) -> bool:
    return getattr(rec, "errorCode", 0) == 0 and getattr(rec, "vignetteCode", 0) == 0