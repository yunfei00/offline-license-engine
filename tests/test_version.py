from __future__ import annotations

import ole

def test_version_exists() -> None:
    assert hasattr(ole, "__version__")
