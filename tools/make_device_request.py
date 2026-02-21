from __future__ import annotations
import argparse
import json
import os
import platform
import uuid
from datetime import datetime

from app.machine_id import calc_machine_id, get_machine_fingerprint_raw

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=".", help="输出目录（默认当前目录）")
    ap.add_argument("--product", default="your_app")
    ap.add_argument("--tool_version", default="1.0.0")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    req = {
        "schema": "req-v1",
        "product": args.product,
        "request_id": str(uuid.uuid4()),
        "machine_id": calc_machine_id(),
        "device_name": platform.node(),
        "os": f"{platform.system()} {platform.release()}",
        "tool_version": args.tool_version,
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "fingerprint_raw": get_machine_fingerprint_raw(),
    }

    fname = f"REQ-{datetime.utcnow().strftime('%Y%m%d')}-{req['request_id'][:8].upper()}.json"
    out_path = os.path.join(args.outdir, fname)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(req, f, ensure_ascii=False, indent=2)

    print("OK:", out_path)
    print("machine_id:", req["machine_id"])

if __name__ == "__main__":
    main()
