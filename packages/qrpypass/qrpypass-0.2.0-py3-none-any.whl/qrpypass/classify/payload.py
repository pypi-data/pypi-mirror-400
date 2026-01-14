from __future__ import annotations

import re
import urllib.parse
from typing import Optional, Dict, Any

from .models import ClassifiedPayload, PayloadKind


_URL_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://")
_BARE_DOMAIN_RE = re.compile(r"^[A-Za-z0-9.-]+\.[A-Za-z]{2,}([/:?#].*)?$")


def classify_payload(raw: str) -> ClassifiedPayload:
    s = (raw or "").strip()

    if not s:
        return ClassifiedPayload(kind=PayloadKind.TEXT, raw="")

    # 1) otpauth provisioning
    if s.lower().startswith("otpauth://"):
        meta = _parse_otpauth_meta_best_effort(s)
        return ClassifiedPayload(kind=PayloadKind.OTPAUTH, raw=s, meta=meta)

    # 2) URL (http/https or bare domain)
    url = _normalize_url_if_possible(s)
    if url is not None:
        return ClassifiedPayload(kind=PayloadKind.URL, raw=s, normalized_url=url, meta=_url_meta(url))

    # 3) Anything else
    return ClassifiedPayload(kind=PayloadKind.TEXT, raw=s)


def _normalize_url_if_possible(s: str) -> Optional[str]:
    # Already has a scheme (http/https/etc.)
    if _URL_SCHEME_RE.match(s):
        return s

    # Looks like a domain.tld (optionally with path/query)
    if _BARE_DOMAIN_RE.match(s):
        return "https://" + s

    return None


def _url_meta(url: str) -> Dict[str, Any]:
    try:
        p = urllib.parse.urlparse(url)
        return {
            "scheme": p.scheme,
            "host": p.hostname or "",
            "path": p.path or "",
        }
    except Exception:
        return {}


def _parse_otpauth_meta_best_effort(uri: str) -> Dict[str, Any]:
    """
    Parse just enough for classification/UI without depending on the OTP module.
    Full parsing + validation belongs in the authenticator module later.
    """
    out: Dict[str, Any] = {}
    try:
        p = urllib.parse.urlparse(uri)
        out["type"] = p.netloc  # totp / hotp (we mainly support totp)
        label = urllib.parse.unquote(p.path.lstrip("/"))
        out["label"] = label

        if ":" in label:
            issuer_label, name = label.split(":", 1)
            out["issuer_label"] = issuer_label
            out["name"] = name
        else:
            out["name"] = label

        qs = urllib.parse.parse_qs(p.query)
        if "issuer" in qs:
            out["issuer"] = qs["issuer"][0]
        if "digits" in qs:
            out["digits"] = qs["digits"][0]
        if "period" in qs:
            out["period"] = qs["period"][0]
        if "algorithm" in qs:
            out["algorithm"] = qs["algorithm"][0]
        # do NOT include secret in meta by default (avoid accidental logging)
        out["has_secret"] = "secret" in qs and bool(qs["secret"][0])
    except Exception:
        # best-effort only
        pass
    return out
