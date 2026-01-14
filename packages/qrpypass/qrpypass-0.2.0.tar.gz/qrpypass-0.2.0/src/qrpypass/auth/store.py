from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Optional, Any, List

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from .models import OTPAuthAccount


class StoreError(RuntimeError):
    pass


def default_store_path() -> Path:
    base = Path(os.environ.get("QRPYPASS_STORE_DIR", Path.home() / ".qrpypass"))
    base.mkdir(parents=True, exist_ok=True)
    return base / "accounts.json"


def _kdf(passphrase: str, salt: bytes) -> bytes:
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    return kdf.derive(passphrase.encode("utf-8", "ignore"))


def _fernet_from_passphrase(passphrase: str, salt: bytes) -> Fernet:
    key = _kdf(passphrase, salt)
    return Fernet(base64_urlsafe(key))


def base64_urlsafe(raw32: bytes) -> bytes:
    import base64
    return base64.urlsafe_b64encode(raw32)


def _serialize_account(a: OTPAuthAccount) -> Dict[str, Any]:
    return {
        "id": a.id,
        "name": a.name,
        "issuer": a.issuer,
        "secret_b32": a.secret_b32,
        "algorithm": a.algorithm,
        "digits": a.digits,
        "period": a.period,
    }


def _deserialize_account(d: Dict[str, Any]) -> OTPAuthAccount:
    return OTPAuthAccount(
        id=d["id"],
        name=d["name"],
        issuer=d.get("issuer"),
        secret_b32=d["secret_b32"],
        algorithm=d.get("algorithm", "SHA1"),
        digits=int(d.get("digits", 6)),
        period=int(d.get("period", 30)),
    )


def load_accounts(path: Optional[Path] = None, *, passphrase: Optional[str] = None) -> Dict[str, OTPAuthAccount]:
    path = path or default_store_path()
    if not path.exists():
        return {}

    raw = path.read_bytes()

    try:
        doc = json.loads(raw.decode("utf-8"))
    except Exception as e:
        raise StoreError(f"Failed to parse store JSON: {e}")

    if doc.get("encrypted") is True:
        if not passphrase:
            raise StoreError("Store is encrypted. Passphrase required.")
        salt_b64 = doc.get("salt_b64")
        token = doc.get("token")
        if not salt_b64 or not token:
            raise StoreError("Encrypted store missing salt/token fields")

        import base64
        salt = base64.b64decode(salt_b64)
        f = _fernet_from_passphrase(passphrase, salt)
        try:
            plain = f.decrypt(token.encode("utf-8"))
        except InvalidToken:
            raise StoreError("Bad passphrase (cannot decrypt store)")
        payload = json.loads(plain.decode("utf-8"))
    else:
        payload = doc

    items = payload.get("accounts", [])
    out: Dict[str, OTPAuthAccount] = {}
    for d in items:
        a = _deserialize_account(d)
        out[a.id] = a
    return out


def save_accounts(accounts: Dict[str, OTPAuthAccount], path: Optional[Path] = None, *, passphrase: Optional[str] = None) -> None:
    path = path or default_store_path()
    payload = {"accounts": [_serialize_account(a) for a in accounts.values()]}

    if passphrase:
        # encrypt at rest
        import base64, os
        salt = os.urandom(16)
        f = _fernet_from_passphrase(passphrase, salt)
        token = f.encrypt(json.dumps(payload).encode("utf-8")).decode("utf-8")
        doc = {
            "encrypted": True,
            "salt_b64": base64.b64encode(salt).decode("utf-8"),
            "token": token,
        }
        path.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    else:
        # plaintext store (still fine for airgapped labs; your call)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
