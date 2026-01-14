from __future__ import annotations

from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np

from .decode import decode_multi, decode_single, QRDecodeError
from .models import QRResult


def _bbox_area(b: Optional[Tuple[int, int, int, int]]) -> int:
    if not b:
        return 10**18
    _, _, w, h = b
    return int(w) * int(h)


def _method_rank(method: str) -> int:
    """
    Lower is better.
    We prefer multi-detection on the full image, then tile, then single.
    """
    m = (method or "").lower()
    if m == "multi":
        return 0
    if m == "tile_multi":
        return 1
    if m == "tile":
        return 2
    if m == "single":
        return 3
    return 9


def _better(a: QRResult, b: QRResult) -> QRResult:
    """
    Return the better of two results for the same payload.
    Priority:
      1) method rank
      2) has bbox/corners
      3) smaller bbox area (tighter localization tends to be more accurate)
    """
    ra, rb = _method_rank(a.method), _method_rank(b.method)
    if ra != rb:
        return a if ra < rb else b

    a_has = (a.bbox is not None) + (a.corners is not None)
    b_has = (b.bbox is not None) + (b.corners is not None)
    if a_has != b_has:
        return a if a_has > b_has else b

    return a if _bbox_area(a.bbox) <= _bbox_area(b.bbox) else b


def scan_qr_anywhere(image_path: str, *, max_results: int = 8) -> List[QRResult]:
    img = cv2.imread(image_path)
    if img is None:
        raise QRDecodeError(f"Image could not be read: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Collect best result per payload
    best: Dict[str, QRResult] = {}

    def consider(r: QRResult):
        if not r.payload:
            return
        cur = best.get(r.payload)
        best[r.payload] = r if cur is None else _better(cur, r)

    # 1) Try full image first
    for r in decode_multi(gray):
        consider(r)
    for r in decode_single(gray):
        consider(r)

    if best:
        # Return best results sorted by quality, capped
        ordered = sorted(best.values(), key=lambda r: (_method_rank(r.method), _bbox_area(r.bbox)))
        return ordered[:max_results]

    # 2) Fallback tiling for large images
    h, w = gray.shape
    tile = 900
    overlap = 200
    step = max(1, tile - overlap)

    for y in range(0, h, step):
        for x in range(0, w, step):
            crop = gray[y:y + tile, x:x + tile]

            # Prefer multi on tile first
            tile_hits = decode_multi(crop)
            for r in tile_hits:
                mapped_bbox = None
                mapped_corners = None

                if r.bbox:
                    bx, by, bw, bh = r.bbox
                    mapped_bbox = (x + bx, y + by, bw, bh)

                if r.corners is not None:
                    mapped_corners = r.corners.copy()
                    mapped_corners[:, 0] += x
                    mapped_corners[:, 1] += y

                consider(QRResult(
                    payload=r.payload,
                    corners=mapped_corners,
                    bbox=mapped_bbox,
                    method="tile_multi"
                ))

            # Then single on tile
            tile_hits2 = decode_single(crop)
            for r in tile_hits2:
                mapped_bbox = None
                mapped_corners = None

                if r.bbox:
                    bx, by, bw, bh = r.bbox
                    mapped_bbox = (x + bx, y + by, bw, bh)

                if r.corners is not None:
                    mapped_corners = r.corners.copy()
                    mapped_corners[:, 0] += x
                    mapped_corners[:, 1] += y

                consider(QRResult(
                    payload=r.payload,
                    corners=mapped_corners,
                    bbox=mapped_bbox,
                    method="tile"
                ))

            if len(best) >= max_results:
                ordered = sorted(best.values(), key=lambda r: (_method_rank(r.method), _bbox_area(r.bbox)))
                return ordered[:max_results]

    ordered = sorted(best.values(), key=lambda r: (_method_rank(r.method), _bbox_area(r.bbox)))
    return ordered[:max_results]


def decode_first(image_path: str) -> str:
    hits = scan_qr_anywhere(image_path, max_results=1)
    if not hits:
        raise QRDecodeError("No QR code found.")
    return hits[0].payload
