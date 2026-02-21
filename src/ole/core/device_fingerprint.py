from __future__ import annotations

import hashlib
import json
import platform
from typing import Any


def gather_fingerprint_inputs() -> dict[str, Any]:
    """Collect host attributes used to derive a device fingerprint."""
    return {
        "hostname": platform.node(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
        },
    }


def compute_fingerprint(fingerprint_inputs: dict[str, Any], nonce: str) -> str:
    """Compute a stable SHA-256 fingerprint from inputs and nonce."""
    payload = {"fingerprint_inputs": fingerprint_inputs, "nonce": nonce}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
