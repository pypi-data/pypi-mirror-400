from __future__ import annotations

import hashlib
import re
import urllib.parse
from typing import Optional, Tuple, Dict

from .models import OTPAuthAccount


class OTPAuthError(ValueError):
    pass


_B32_RE = re.compile(r"^[A-Z2-7]+=*$")


def _norm_b32(s: str) -> str:
    s2 = s.strip().replace(" ", "").upper()
    if not s2:
        raise OTPAuthError("Missing secret")
    # allow lowercase + spaces in input, normalize to uppercase
    if not _B32_RE.match(s2):
        # We keep it strict-ish: otpauth secrets are base32 (A-Z2-7) with optional '=' padding.
        raise OTPAuthError("Secret does not look like base32")
    return s2


def _parse_label(label: str) -> Tuple[Optional[str], str]:
    """
    Label is usually 'Issuer:AccountName' or just 'AccountName'.
    """
    label = label.strip()
    if ":" in label:
        issuer_label, name = label.split(":", 1)
        issuer_label = issuer_label.strip() or None
        name = name.strip()
        return issuer_label, name
    return None, label


def _stable_id(issuer: Optional[str], name: str) -> str:
    base = f"{issuer or ''}|{name}".encode("utf-8", "ignore")
    return hashlib.sha256(base).hexdigest()[:16]


def parse_otpauth_uri(uri: str) -> OTPAuthAccount:
    """
    Supports otpauth://totp/... only. HOTP can be added later.
    """
    if not uri or not uri.lower().startswith("otpauth://"):
        raise OTPAuthError("Not an otpauth URI")

    p = urllib.parse.urlparse(uri)
    typ = (p.netloc or "").lower()
    if typ != "totp":
        raise OTPAuthError(f"Unsupported otpauth type: {typ!r} (only 'totp' supported)")

    label = urllib.parse.unquote((p.path or "").lstrip("/"))
    if not label:
        raise OTPAuthError("Missing label in otpauth URI")

    issuer_label, name = _parse_label(label)
    if not name:
        raise OTPAuthError("Missing account name in label")

    qs = urllib.parse.parse_qs(p.query)

    secret_raw = (qs.get("secret", [""])[0] or "").strip()
    secret_b32 = _norm_b32(secret_raw)

    issuer_q = (qs.get("issuer", [None])[0] or None)
    issuer = issuer_q or issuer_label

    algorithm = (qs.get("algorithm", ["SHA1"])[0] or "SHA1").upper()
    if algorithm not in {"SHA1", "SHA256", "SHA512"}:
        raise OTPAuthError(f"Unsupported algorithm: {algorithm}")

    digits_s = (qs.get("digits", ["6"])[0] or "6")
    try:
        digits = int(digits_s)
    except ValueError:
        raise OTPAuthError("digits must be an integer")
    if digits not in {6, 7, 8}:
        raise OTPAuthError("digits must be 6, 7, or 8")

    period_s = (qs.get("period", ["30"])[0] or "30")
    try:
        period = int(period_s)
    except ValueError:
        raise OTPAuthError("period must be an integer")
    if period < 5 or period > 300:
        raise OTPAuthError("period must be between 5 and 300 seconds")

    acc_id = _stable_id(issuer, name)

    return OTPAuthAccount(
        id=acc_id,
        name=name,
        issuer=issuer,
        secret_b32=secret_b32,
        algorithm=algorithm,
        digits=digits,
        period=period,
    )
