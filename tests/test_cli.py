from __future__ import annotations

from ole.cli.main import app

def test_cli_imports() -> None:
    assert app is not None
