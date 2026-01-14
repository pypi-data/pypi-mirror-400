from __future__ import annotations
from typing import List, Tuple
import cv2
import numpy as np
from .models import QRResult

class QRDecodeError(RuntimeError):
    pass

def _bbox_from_corners(corners: np.ndarray) -> Tuple[int, int, int, int]:
    xs, ys = corners[:, 0], corners[:, 1]
    x0, y0 = int(xs.min()), int(ys.min())
    x1, y1 = int(xs.max()), int(ys.max())
    return x0, y0, max(1, x1-x0), max(1, y1-y0)

def decode_multi(img: np.ndarray) -> List[QRResult]:
    det = cv2.QRCodeDetector()
    try:
        ok, data_list, points, _ = det.detectAndDecodeMulti(img)
    except Exception:
        return []
    if not ok or not data_list:
        return []
    results = []
    for i, data in enumerate(data_list):
        if not data:
            continue
        corners = points[i].astype(np.float32) if points is not None else None
        bbox = _bbox_from_corners(corners) if corners is not None else None
        results.append(QRResult(payload=data, corners=corners, bbox=bbox, method="multi"))
    return results

def decode_single(img: np.ndarray) -> List[QRResult]:
    det = cv2.QRCodeDetector()
    data, pts, _ = det.detectAndDecode(img)
    if not data:
        return []
    corners = pts.astype(np.float32) if pts is not None else None
    bbox = _bbox_from_corners(corners) if corners is not None else None
    return [QRResult(payload=data, corners=corners, bbox=bbox, method="single")]
