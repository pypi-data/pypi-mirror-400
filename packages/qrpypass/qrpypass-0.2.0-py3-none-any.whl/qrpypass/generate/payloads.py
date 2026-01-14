from __future__ import annotations

from typing import Dict, Any, Optional
from urllib.parse import urlencode, quote

from qrpypass.auth.generate import generate_totp_secret_b32, build_otpauth_uri
from .models import GenKind, GeneratedPayload


def generate_text(*, text: str) -> GeneratedPayload:
    text = (text or "").strip()
    if not text:
        raise ValueError("text is required")
    return GeneratedPayload(kind=GenKind.TEXT, payload=text, meta={})


def generate_url(*, url: str) -> GeneratedPayload:
    url = (url or "").strip()
    if not url:
        raise ValueError("url is required")
    # Do not over-normalize; generation should respect user intent.
    return GeneratedPayload(kind=GenKind.URL, payload=url, meta={})


def generate_totp(
    *,
    issuer: str,
    account_name: str,
    secret_b32: Optional[str] = None,
    digits: int = 6,
    period: int = 30,
    algorithm: str = "SHA1",
    nbytes: int = 20,
) -> GeneratedPayload:
    issuer = (issuer or "").strip()
    account_name = (account_name or "").strip()
    if not issuer:
        raise ValueError("issuer is required")
    if not account_name:
        raise ValueError("account_name is required")

    if secret_b32 is None:
        if nbytes < 10 or nbytes > 64:
            raise ValueError("nbytes must be between 10 and 64")
        secret_b32 = generate_totp_secret_b32(nbytes=nbytes)

    uri = build_otpauth_uri(
        issuer=issuer,
        account_name=account_name,
        secret_b32=secret_b32,
        digits=digits,
        period=period,
        algorithm=algorithm,
    )

    # meta includes secret because you are generating it; caller can choose to display/store
    return GeneratedPayload(
        kind=GenKind.OTPAUTH_TOTP,
        payload=uri,
        meta={
            "issuer": issuer,
            "account_name": account_name,
            "digits": digits,
            "period": period,
            "algorithm": algorithm.upper(),
            "secret_b32": secret_b32,
        },
    )


def generate_payload(kind: str, params: Dict[str, Any]) -> GeneratedPayload:
    k = (kind or "").strip().lower()
    if k == "text":
        return generate_text(text=params.get("text", ""))
    if k == "url":
        return generate_url(url=params.get("url", ""))
    if k in {"totp", "otpauth", "otpauth_totp"}:
        return generate_totp(
            issuer=params.get("issuer", ""),
            account_name=params.get("account_name", ""),
            secret_b32=params.get("secret_b32"),
            digits=int(params.get("digits", 6)),
            period=int(params.get("period", 30)),
            algorithm=params.get("algorithm", "SHA1"),
            nbytes=int(params.get("nbytes", 20)),
        )
    raise ValueError(f"Unsupported kind: {kind!r}")
