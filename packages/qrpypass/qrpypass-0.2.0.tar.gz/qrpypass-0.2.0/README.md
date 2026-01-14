![qr-pypass logo](images/qr-logo.png)

# qr-pypass

**qr-pypass** is a lightweight, headless QR decoding and TOTP authentication service built for **offline-first security workflows**.

It is designed for air-gapped labs, red-team and blue-team tooling, automation pipelines, and environments where QR codes and 2FA need to be processed **locally**, without mobile devices or cloud dependencies.

**Homepage:** [https://ginkorea.one](https://ginkorea.one)
**Source:** [https://github.com/ginkorea/qr-pypass](https://github.com/ginkorea/qr-pypass)
**PyPI:** [https://pypi.org/project/qrpypass/](https://pypi.org/project/qrpypass/)

---

## What It Does

With `qr-pypass`, you can:

* Decode QR codes from screenshots or images
* Detect and classify QR payloads (URL, text, otpauth)
* Generate QR codes programmatically
* Generate, import, store, and verify TOTP (RFC 6238) secrets
* Run everything locally with no outbound network access

The project exposes both:

* A **Python API** for direct integration
* A **Flask-based HTTP service** with a minimal web UI

---

## Core Features

### QR Decoding

* Detects **multiple QR codes anywhere in an image**
* Uses OpenCV with multi-pass detection and tiling fallback
* Returns bounding boxes, corner points, and decode method
* Robust against screenshots, partial QRs, and large images

### Payload Classification

Automatically classifies decoded payloads as:

* `url` (with normalization)
* `text`
* `otpauth` (TOTP provisioning URIs)

### TOTP / OTPAuth

* Generate RFC-compliant `otpauth://totp` URIs
* Import existing provisioning URIs
* Secure local storage (optional encryption at rest)
* Generate current TOTP codes
* Verify TOTP codes with configurable time window

### QR Generation

* Generate QR codes for:

  * URLs
  * Arbitrary text
  * TOTP provisioning URIs
* Control box size and border
* Outputs PNG images

### Service and Web UI

* Flask-based HTTP API
* Minimal web UI for:

  * Uploading screenshots or images
  * Viewing decoded QR payloads
  * Generating QR codes
  * Managing stored TOTP accounts

No JavaScript frameworks. No external assets.

---

## Installation

### From PyPI

```bash
pip install qrpypass
```

Python **3.9+** is required.

---

### From Source (Development)

```bash
git clone https://github.com/ginkorea/qr-pypass.git
cd qr-pypass

python -m venv .qr-env
source .qr-env/bin/activate

pip install -r requirements.txt
pip install -e .
```

---

## Running the Service

```bash
python -m qrpypass.service.run
```

By default, the service runs at:

```
http://127.0.0.1:5000
```

---

## Configuration

The service can be configured using environment variables:

| Variable             | Default       | Description                     |
| -------------------- | ------------- | ------------------------------- |
| `QRPYPASS_HOST`      | `127.0.0.1`   | Bind address                    |
| `QRPYPASS_PORT`      | `5000`        | Port                            |
| `QRPYPASS_DEBUG`     | `0`           | Enable Flask debug mode         |
| `QRPYPASS_STORE_DIR` | `~/.qrpypass` | Local account storage directory |

---

## Web UI Routes

* `/` – QR scan UI (upload screenshots or images)
* `/gen` – QR payload and TOTP generator
* `/vault` – Stored TOTP account management

---

## API Overview

### Health Check

```http
GET /health
```

---

### Scan QR Codes

```http
POST /scan
Content-Type: multipart/form-data
```

**Form fields**

* `file` (required) – image file
* `max_results` (optional, default: 8)

---

### Generate Payload

```http
POST /gen/payload
Content-Type: application/json
```

```json
{
  "kind": "url | text | totp",
  "params": { },
  "import": false,
  "passphrase": null
}
```

---

### Generate QR Image

```http
POST /gen/qr
Content-Type: application/json
```

```json
{
  "payload": "...",
  "box_size": 8,
  "border": 2
}
```

Returns `image/png`.

---

### TOTP Endpoints

| Endpoint            | Description           |
| ------------------- | --------------------- |
| `POST /auth/import` | Import otpauth URI    |
| `GET /auth/list`    | List stored accounts  |
| `GET /auth/code`    | Get current TOTP code |
| `POST /auth/verify` | Verify TOTP code      |

An optional `passphrase` encrypts the TOTP store at rest.

---

## Python API Example

```python
from qrpypass.qr import scan_and_classify

hits = scan_and_classify("screenshot.png")
for hit in hits:
    print(hit.classification.kind, hit.qr.payload)
```

---

## Testing

End-to-end tests are included:

```bash
python test/api-test.py
python test/full_api_smoke.py
python test/test_totp_verify_flow.py
```

These cover:

* QR generation → scan → classification
* TOTP generation, import, code generation, and verification

---

## Security Notes

* Secrets are never logged
* TOTP storage can be encrypted at rest
* No outbound network access
* Suitable for air-gapped or lab environments

---

## Common Use Cases

* QR extraction from screenshots (2FA enrollment, phishing analysis)
* Headless TOTP verification in security tooling
* Red-team and blue-team labs
* Offline QR decoding pipelines
* Local alternatives to mobile authenticator apps

---

## License

MIT

---

## Author

**Josh Gompert**
[https://ginkorea.one](https://ginkorea.one)

