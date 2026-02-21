from __future__ import annotations
"""
Offline local concurrency limiter (single machine).

Implements "max_concurrency" by taking one of N lock slots.
"""

import os
import sys
from dataclasses import dataclass
from platformdirs import user_state_dir

class ConcurrencyError(RuntimeError):
    pass

@dataclass
class SlotHandle:
    slot_index: int
    path: str
    _fh: object

def _try_lock_file(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fh = open(path, "a+b")
    try:
        if sys.platform.startswith("win"):
            import msvcrt
            try:
                msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError:
                fh.close()
                return None
        else:
            import fcntl
            try:
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                fh.close()
                return None
        return fh
    except Exception:
        try:
            fh.close()
        except Exception:
            pass
        return None

def acquire_concurrency_slot(app_name: str, max_concurrency: int) -> SlotHandle | None:
    if not max_concurrency or max_concurrency <= 0:
        return None

    state_dir = user_state_dir(app_name)
    lock_dir = os.path.join(state_dir, "locks")
    os.makedirs(lock_dir, exist_ok=True)

    for i in range(int(max_concurrency)):
        path = os.path.join(lock_dir, f"slot_{i}.lock")
        fh = _try_lock_file(path)
        if fh is not None:
            try:
                fh.seek(0)
                fh.truncate()
                fh.write(str(os.getpid()).encode("utf-8"))
                fh.flush()
            except Exception:
                pass
            return SlotHandle(slot_index=i, path=path, _fh=fh)

    raise ConcurrencyError(f"已达到最大并发数限制：max_concurrency={max_concurrency}（同机并发）")
