from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any


class PayloadKind(str, Enum):
    OTPAUTH = "otpauth"
    URL = "url"
    TEXT = "text"


@dataclass(frozen=True)
class ClassifiedPayload:
    kind: PayloadKind
    raw: str
    # For URL kind, normalized_url will include a scheme.
    normalized_url: Optional[str] = None
    # Extra extracted info (issuer/name for otpauth label, etc.)
    meta: Optional[Dict[str, Any]] = None

    def to_dict(self) -> dict:
        return {
            "kind": self.kind.value,
            "raw": self.raw,
            "normalized_url": self.normalized_url,
            "meta": self.meta or {},
        }
