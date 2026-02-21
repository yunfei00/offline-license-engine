import hashlib
import platform
import sys

def _win_machine_guid() -> str:
    """
    Windows: read MachineGuid from registry.
    """
    import winreg
    key = winreg.OpenKey(
        winreg.HKEY_LOCAL_MACHINE,
        r"SOFTWARE\Microsoft\Cryptography"
    )
    value, _ = winreg.QueryValueEx(key, "MachineGuid")
    return str(value).strip()

def get_machine_fingerprint_raw() -> str:
    """
    Raw fingerprint string used to derive machine_id.
    IMPORTANT: don't change the fields after shipping, or old licenses will break.
    """
    parts = []
    parts.append(f"os={sys.platform}")
    parts.append(f"arch={platform.machine()}")
    parts.append(f"cpu={platform.processor()}")

    if sys.platform.startswith("win"):
        parts.append(f"guid={_win_machine_guid()}")
    else:
        parts.append(f"node={platform.node()}")  # fallback

    return "|".join(parts)

def calc_machine_id() -> str:
    raw = get_machine_fingerprint_raw().encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()
