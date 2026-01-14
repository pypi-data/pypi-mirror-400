#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:5000"

def post_json(path: str, obj: dict) -> dict:
    url = BASE + path
    req = Request(url, data=json.dumps(obj).encode("utf-8"), headers={"Content-Type":"application/json"}, method="POST")
    with urlopen(req, timeout=20) as r:
        data = json.loads(r.read().decode("utf-8"))
        if r.status >= 400:
            raise RuntimeError(f"{path} -> HTTP {r.status}: {data}")
        return data

def get_json(path: str) -> dict:
    url = BASE + path
    req = Request(url, method="GET")
    with urlopen(req, timeout=20) as r:
        data = json.loads(r.read().decode("utf-8"))
        if r.status >= 400:
            raise RuntimeError(f"{path} -> HTTP {r.status}: {data}")
        return data

def main():
    # 1) generate a totp otpauth URI (no import)
    gen = post_json("/gen/payload", {
        "kind": "totp",
        "params": {"issuer":"QRPYPASS", "account_name":"verify-test@local", "digits":6, "period":30, "algorithm":"SHA1"},
        "import": False
    })
    uri = gen["generated"]["payload"]
    print("[gen] uri:", uri[:80] + "...")

    # 2) import it
    imp = post_json("/auth/import", {"otpauth_uri": uri})
    acc_id = imp["imported"]["id"]
    print("[import] id:", acc_id)

    # 3) get current code
    code_resp = get_json(f"/auth/code?id={acc_id}")
    code = code_resp["code"]
    print("[code] code:", code, "remaining:", code_resp["seconds_remaining"])

    # 4) verify the code
    ver = post_json("/auth/verify", {"id": acc_id, "code": code, "window": 1})
    print("[verify] ok:", ver["ok"], "offset:", ver["matched_offset"])
    if not ver["ok"]:
        raise RuntimeError("Expected verify to succeed")

    # 5) verify a bad code
    bad = post_json("/auth/verify", {"id": acc_id, "code": "000000", "window": 1})
    print("[verify-bad] ok:", bad["ok"])
    if bad["ok"]:
        raise RuntimeError("Expected verify to fail")

    print("All good.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("FAIL:", e, file=sys.stderr)
        raise
