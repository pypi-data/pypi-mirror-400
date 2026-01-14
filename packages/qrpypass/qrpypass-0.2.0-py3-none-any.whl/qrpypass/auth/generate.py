from __future__ import annotations

import base64
import os
from urllib.parse import quote


def generate_totp_secret_b32(*, nbytes: int = 20) -> str:
    """
    Generate a random TOTP secret in Base32 (uppercase, no padding).
    Default: 20 bytes (160-bit), common for TOTP.
    """
    if not (10 <= nbytes <= 64):
        raise ValueError("nbytes must be between 10 and 64")

    raw = os.urandom(nbytes)
    # base32 includes '=', strip padding for otpauth URIs
    return base64.b32encode(raw).decode("ascii").rstrip("=").upper()


def build_otpauth_uri(
    *,
    issuer: str,
    account_name: str,
    secret_b32: str,
    digits: int = 6,
    period: int = 30,
    algorithm: str = "SHA1",
) -> str:
    """
    Build an otpauth://totp provisioning URI.

    Label: "Issuer:Account"
    Query: secret, issuer, algorithm, digits, period
    """
    issuer = (issuer or "").strip()
    account_name = (account_name or "").strip()
    secret_b32 = (secret_b32 or "").strip().replace(" ", "").upper()

    if not issuer:
        raise ValueError("issuer is required")
    if not account_name:
        raise ValueError("account_name is required")
    if not secret_b32:
        raise ValueError("secret_b32 is required")

    algorithm = (algorithm or "SHA1").upper()
    if algorithm not in {"SHA1", "SHA256", "SHA512"}:
        raise ValueError("algorithm must be SHA1, SHA256, or SHA512")

    if digits not in {6, 7, 8}:
        raise ValueError("digits must be 6, 7, or 8")
    if not (5 <= int(period) <= 300):
        raise ValueError("period must be between 5 and 300 seconds")

    # Label is commonly "Issuer:Account"
    label = f"{issuer}:{account_name}"
    label_enc = quote(label, safe="")

    return (
        f"otpauth://totp/{label_enc}"
        f"?secret={quote(secret_b32, safe='')}"
        f"&issuer={quote(issuer, safe='')}"
        f"&algorithm={quote(algorithm, safe='')}"
        f"&digits={int(digits)}"
        f"&period={int(period)}"
    )
