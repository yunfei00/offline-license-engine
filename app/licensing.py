from __future__ import annotations

import base64
import json
import os
from platformdirs import user_config_dir

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

from .machine_id import calc_machine_id
from .concurrency import acquire_concurrency_slot, ConcurrencyError

PUBLIC_KEY_B64 = "REPLACE_WITH_YOUR_PUBLIC_KEY_B64"

APP_NAME = "YourApp"
LICENSE_FILENAME = "license.lic"
ENV_LICENSE_PATH = "YOURAPP_LICENSE_PATH"

class LicenseError(RuntimeError):
    pass

def _candidate_license_paths():
    paths = []
    env_path = os.environ.get(ENV_LICENSE_PATH)
    if env_path:
        paths.append(env_path)

    try:
        exe_dir = os.path.dirname(os.path.abspath(os.sys.argv[0]))
        paths.append(os.path.join(exe_dir, LICENSE_FILENAME))
    except Exception:
        pass

    cfg_dir = user_config_dir(APP_NAME)
    paths.append(os.path.join(cfg_dir, LICENSE_FILENAME))

    seen = set()
    uniq = []
    for p in paths:
        if p and p not in seen:
            uniq.append(p)
            seen.add(p)
    return uniq

def _load_license_file() -> tuple[str, dict]:
    for p in _candidate_license_paths():
        if p and os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as f:
                return p, json.load(f)
    raise LicenseError(
        "未找到 license 文件。\\n"
        f"请将 {LICENSE_FILENAME} 放到：程序同目录 或 用户配置目录，"
        f"或设置环境变量 {ENV_LICENSE_PATH} 指向license路径。"
    )

def _stable_payload_bytes(lic_no_sig: dict) -> bytes:
    return json.dumps(lic_no_sig, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def _verify_signature(lic: dict) -> dict:
    lic = dict(lic)
    sig_b64 = lic.pop("signature", None)
    if not sig_b64:
        raise LicenseError("License 缺少 signature 字段")

    payload = _stable_payload_bytes(lic)
    try:
        vk = VerifyKey(base64.b64decode(PUBLIC_KEY_B64))
        vk.verify(payload, base64.b64decode(sig_b64))
    except BadSignatureError:
        raise LicenseError("License 签名无效（文件被篡改或非官方签发）")
    except Exception as e:
        raise LicenseError(f"License 校验失败：{e}")

    return lic

def _verify_rules(lic: dict) -> dict:
    schema = lic.get("schema", "lic-v1")
    if schema not in ("lic-v1",):
        raise LicenseError(f"License schema 不支持：{schema}")

    if lic.get("product") != "your_app":
        raise LicenseError("License 产品不匹配")

    if lic.get("type") != "perpetual":
        raise LicenseError("License 不是永久授权")

    current = calc_machine_id()
    device_ids = lic.get("device_ids")
    if isinstance(device_ids, list) and device_ids:
        if current not in device_ids:
            raise LicenseError("License 与当前机器不匹配：该授权不包含本机设备授权（device_ids 白名单）。")
    else:
        expected = lic.get("machine_id")
        if not expected:
            raise LicenseError("License 未绑定机器（machine_id / device_ids 缺失）")
        if expected != current:
            raise LicenseError("License 与当前机器不匹配：该授权仅允许在原授权机器上运行。")
    return lic

def ensure_licensed() -> dict:
    path, lic = _load_license_file()
    lic2 = _verify_signature(lic)
    lic3 = _verify_rules(lic2)

    max_concurrency = lic3.get("max_concurrency")
    try:
        ch = acquire_concurrency_slot(APP_NAME, int(max_concurrency)) if max_concurrency is not None else None
    except ConcurrencyError as e:
        raise LicenseError(str(e))

    return {
        "schema": lic3.get("schema", "lic-v1"),
        "license_id": lic3.get("license_id", ""),
        "license_path": path,
        "customer": lic3.get("customer", ""),
        "customer_type": lic3.get("customer_type", ""),
        "customer_id": lic3.get("customer_id", ""),
        "type": lic3.get("type", ""),
        "features": lic3.get("features", []),
        "machine_id": calc_machine_id(),
        "issued_at": lic3.get("issued_at", ""),
        "product": lic3.get("product", ""),
        "device_ids": lic3.get("device_ids", []),
        "seat_count": lic3.get("seat_count", None),
        "max_concurrency": max_concurrency,
        "concurrency_handle": ch,
    }
