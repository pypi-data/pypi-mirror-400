from __future__ import annotations

import base64
import binascii
import hmac
import hashlib
import time
from typing import Tuple

from .models import OTPAuthAccount  # canonical


def _b32_decode_nopad(secret_b32: str) -> bytes:
    s = (secret_b32 or "").strip().replace(" ", "").upper()
    pad = (-len(s)) % 8
    s += "=" * pad
    try:
        return base64.b32decode(s, casefold=True)
    except binascii.Error as e:
        raise ValueError("Invalid base32 secret") from e


def _hotp(key: bytes, counter: int, digits: int, algo: str) -> str:
    algo_u = (algo or "SHA1").upper()
    if algo_u == "SHA1":
        digestmod = hashlib.sha1
    elif algo_u == "SHA256":
        digestmod = hashlib.sha256
    elif algo_u == "SHA512":
        digestmod = hashlib.sha512
    else:
        raise ValueError("Unsupported algorithm (use SHA1/SHA256/SHA512)")

    msg = counter.to_bytes(8, "big")
    h = hmac.new(key, msg, digestmod).digest()
    off = h[-1] & 0x0F
    dbc = int.from_bytes(h[off:off + 4], "big") & 0x7FFFFFFF
    code = dbc % (10 ** digits)
    return str(code).zfill(digits)


def totp_at(acc: OTPAuthAccount, for_time: int) -> str:
    key = _b32_decode_nopad(acc.secret_b32)
    period = int(acc.period)
    counter = int(for_time) // period
    return _hotp(key, counter, int(acc.digits), acc.algorithm)


def totp_now(acc: OTPAuthAccount) -> Tuple[str, int]:
    now = int(time.time())
    code = totp_at(acc, now)
    period = int(acc.period)
    remaining = period - (now % period)
    return code, remaining


def totp_verify(
    acc: OTPAuthAccount,
    code: str,
    *,
    window: int = 1,
    at_time: int | None = None,
) -> Tuple[bool, int]:
    if at_time is None:
        at_time = int(time.time())

    code = (code or "").strip()
    if not code.isdigit():
        return False, 0

    if window < 0 or window > 10:
        raise ValueError("window must be between 0 and 10")

    period = int(acc.period)
    base = int(at_time)

    for offset in range(-window, window + 1):
        t = base + (offset * period)
        expected = totp_at(acc, t)
        if hmac.compare_digest(expected, code):
            return True, offset

    return False, 0
