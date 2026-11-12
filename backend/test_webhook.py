import hashlib
import hmac
import json
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()
secret = os.environ["WEBHOOK_SECRET"].encode()
bug = sys.argv[1] if len(sys.argv) > 1 else "clipped-button"

payload = json.dumps({"after": "abc123def456", "ref": "refs/heads/main"}).encode()
signature = "sha256=" + hmac.new(secret, payload, hashlib.sha256).hexdigest()

r = requests.post(
    f"http://localhost:8000/webhook/github?bug={bug}",
    data=payload,
    headers={"X-Hub-Signature-256": signature, "Content-Type": "application/json"},
)
print(r.status_code, r.json())