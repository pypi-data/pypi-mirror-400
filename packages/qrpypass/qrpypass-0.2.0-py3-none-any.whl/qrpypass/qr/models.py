from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple, List
import numpy as np

@dataclass(frozen=True)
class QRResult:
    payload: str
    corners: Optional[np.ndarray] = None
    bbox: Optional[Tuple[int, int, int, int]] = None
    method: str = "unknown"

    def to_dict(self) -> dict:
        d = {"payload": self.payload, "method": self.method}
        if self.bbox:
            x, y, w, h = self.bbox
            d["bbox"] = {"x": x, "y": y, "w": w, "h": h}
        if self.corners is not None:
            d["corners"] = self.corners.astype(float).tolist()
        return d
