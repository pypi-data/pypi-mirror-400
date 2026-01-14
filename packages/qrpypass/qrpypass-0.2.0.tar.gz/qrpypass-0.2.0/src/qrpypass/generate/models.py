from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any


class GenKind(str, Enum):
    URL = "url"
    TEXT = "text"
    OTPAUTH_TOTP = "otpauth_totp"


@dataclass(frozen=True)
class GeneratedPayload:
    kind: GenKind
    payload: str
    meta: Dict[str, Any]

    def to_dict(self) -> dict:
        return {"kind": self.kind.value, "payload": self.payload, "meta": self.meta}
