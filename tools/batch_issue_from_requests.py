from __future__ import annotations
import argparse
import base64
import glob
import json
import os
import uuid
from datetime import date

from nacl.signing import SigningKey

def _stable_payload_bytes(d: dict) -> bytes:
    return json.dumps(d, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--private_key_b64", required=True)
    ap.add_argument("--requests_dir", required=True, help="存放 REQ-*.json 的目录")
    ap.add_argument("--out", default="license.lic")
    ap.add_argument("--product", default="your_app")
    ap.add_argument("--features", default="all", help='comma-separated, e.g. "basic,export_pdf"')
    ap.add_argument("--customer", default="", help="展示名称；默认使用目录名")
    ap.add_argument("--customer_type", default="account")
    ap.add_argument("--customer_id", default="", help="内部追溯ID；默认自动生成 acct_<uuid8>")
    ap.add_argument("--max_concurrency", default="", help="integer, single-machine max concurrent processes")
    args = ap.parse_args()

    req_dir = args.requests_dir
    if not os.path.isdir(req_dir):
        raise SystemExit(f"requests_dir 不存在：{req_dir}")

    files = sorted(glob.glob(os.path.join(req_dir, "*.json")))
    if not files:
        raise SystemExit(f"目录中未找到 .json 请求文件：{req_dir}")

    machine_ids = []
    bad = []
    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8") as f:
                req = json.load(f)
            mid = (req.get("machine_id") or "").strip()
            prod = (req.get("product") or "").strip()
            schema = (req.get("schema") or "").strip()
            if schema != "req-v1":
                bad.append((os.path.basename(fp), f"schema={schema}"))
                continue
            if prod and prod != args.product:
                bad.append((os.path.basename(fp), f"product mismatch: {prod}"))
                continue
            if not mid:
                bad.append((os.path.basename(fp), "missing machine_id"))
                continue
            machine_ids.append(mid)
        except Exception as e:
            bad.append((os.path.basename(fp), str(e)))

    seen = set()
    device_ids = []
    for mid in machine_ids:
        if mid not in seen:
            device_ids.append(mid)
            seen.add(mid)

    if not device_ids:
        raise SystemExit("没有收集到有效的 machine_id。请检查请求文件。")

    customer = args.customer.strip() or os.path.basename(os.path.abspath(req_dir))
    customer_id = args.customer_id.strip() or ("acct_" + uuid.uuid4().hex[:8])
    features = [x.strip() for x in args.features.split(",") if x.strip()]
    license_id = "lic_" + uuid.uuid4().hex[:10]

    lic = {
        "schema": "lic-v1",
        "license_id": license_id,
        "product": args.product,
        "customer": customer,
        "customer_type": args.customer_type,
        "customer_id": customer_id,
        "type": "perpetual",
        "device_ids": device_ids,
        "seat_count": len(device_ids),
        "features": features,
        "issued_at": date.today().isoformat(),
    }

    if args.max_concurrency.strip():
        lic["max_concurrency"] = int(args.max_concurrency.strip())

    sk = SigningKey(base64.b64decode(args.private_key_b64))
    payload = _stable_payload_bytes(lic)
    sig = sk.sign(payload).signature
    lic["signature"] = base64.b64encode(sig).decode("utf-8")

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(lic, f, ensure_ascii=False, indent=2)

    report = {
        "license_id": license_id,
        "customer": customer,
        "customer_id": customer_id,
        "requests_dir": os.path.abspath(req_dir),
        "source_files": [os.path.basename(x) for x in files],
        "bad_files": bad,
        "seat_count": len(device_ids),
    }
    rep_path = os.path.splitext(args.out)[0] + ".report.json"
    with open(rep_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("OK:", args.out)
    print("report:", rep_path)
    print("seat_count:", len(device_ids))
    if bad:
        print("WARN: bad files:", len(bad))

if __name__ == "__main__":
    main()
