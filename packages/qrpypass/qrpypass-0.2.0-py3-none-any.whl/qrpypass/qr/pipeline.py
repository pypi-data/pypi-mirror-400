from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from qrpypass.qr.models import QRResult
from qrpypass.qr.scan import scan_qr_anywhere
from qrpypass.classify import ClassifiedPayload, classify_payload


@dataclass(frozen=True)
class ScanHit:
    qr: QRResult
    classification: ClassifiedPayload

    def to_dict(self) -> Dict[str, Any]:
        return {
            "qr": self.qr.to_dict(),
            "classification": self.classification.to_dict(),
        }


def scan_and_classify(image_path: str, *, max_results: int = 8) -> List[ScanHit]:
    """
    High-level pipeline:
      - find/decode QR(s) anywhere in image
      - classify decoded payload(s)
      - return structured results
    """
    hits = scan_qr_anywhere(image_path, max_results=max_results)
    out: List[ScanHit] = []
    for h in hits:
        c = classify_payload(h.payload)
        out.append(ScanHit(qr=h, classification=c))
    return out
