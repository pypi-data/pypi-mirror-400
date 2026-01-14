
# FabSec SDK (Python)

Python SDK for interacting with the **FabSec Security & AI Platform**.

FabSec helps you send security events (auth/login, requests, suspicious activity) to a backend that can analyze risk and return an `audit_id` (and other results depending on your backend).

---

## Installation

### From PyPI (recommended)

```bash
pip install -U fabsec
```

## From GitHub

pip install git+https://github.com/sudomata/fabsec-python.git

## Local development install

python -m venv venv
source venv/bin/activate
pip install -U pip
pip install -e .

## Quick start


from fabsec import FabSecClient

c = FabSecClient(
    api_key="FABSEC_API_KEY",
    base_url="http://127.0.0.1:8080",  # backend local
)

res = c.ingest({
    "app_id": "my-app",
    "user_id": "user@test.com",
    "route": "/login",
    "method": "POST",
    "ip": "192.168.1.10",
})

print(res["audit_id"])


## Configuration

### API key

##### Set your API key in code:

c = FabSecClient(api_key="FABSEC_API_KEY")

## Base URL

By default, the SDK may target a local backend. You can override it:

c = FabSecClient(
    api_key="FABSEC_API_KEY",
    base_url="http://127.0.0.1:8080",
)
