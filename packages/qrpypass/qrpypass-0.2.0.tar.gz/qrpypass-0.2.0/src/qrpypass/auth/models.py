from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class OTPAuthAccount:
    """
    Parsed representation of otpauth://totp/... provisioning.
    Secret is stored as base32 string (normalized) but should not be logged.
    """
    id: str                 # stable key for storage (derived from issuer+name)
    name: str               # account name (label right side)
    issuer: Optional[str]   # issuer if present
    secret_b32: str         # base32 (no spaces), normalized to uppercase
    algorithm: str = "SHA1" # SHA1/SHA256/SHA512
    digits: int = 6
    period: int = 30

    def safe_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "issuer": self.issuer,
            "algorithm": self.algorithm,
            "digits": self.digits,
            "period": self.period,
        }


# Backwards-compatible alias (your totp.py was importing OTPAccount)
OTPAccount = OTPAuthAccount
