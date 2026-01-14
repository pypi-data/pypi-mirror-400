# FabSec SDK (Python)

## Install (local)

```bash
python -m venv venv
source venv/bin/activate
pip install -U pip
pip install -e .
```


## Installation

```bash
pip install fabsec
```

ou 

pip install git+https://github.com/sudomata/fabsec-python.git


from fabsec import FabSecClient

c = FabSecClient(api_key="FABSEC_API_KEY")

res = c.ingest({
    "app_id": "my-app",
    "user_id": "user@test.com",
    "route": "/login",
    "method": "POST",
    "ip": "192.168.1.10",
})

print(res["audit_id"])
